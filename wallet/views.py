# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponseServerError, \
        HttpResponseNotFound, HttpResponse

from decimal import Decimal
from corelib.http import JsonResponse
from corelib.utils import random_str
from corelib.wechat import OAuth
from corelib.paginator import paginator

from wallet.models import Wallet, WechatSDK, WalletRecharge, get_related_amount, Withdrawals, WalletRecord
from wallet.error_handle import WalletError
from user.models import User


def wallet(request):
    wallet = Wallet.get(user_id=request.user.id)
    return JsonResponse(wallet.to_dict())


def wallet_record(request):
    page = request.POST.get("page", 1)

    record_list = WalletRecord.objects.filter(owner_id=request.user.id)

    results = {"record_list": [], "paginator": {}}
    record_list, paginator_dict = paginator(record_list, page, 30)
    # user_list = [user.basic_info() for user in record_list]
    records = []
    for record in record_list:
        user = User.get(record.owner_id)
        basic_info = user.basic_info()
        basic_info["record_msg"] = "%s - %s" % (user.nickname, record.type)
        basic_info["amount"] = record.amount
        basic_info["type"] = record.type
        basic_info["category"] = record.category

        records.append(basic_info)

    results["paginator"] = paginator_dict
    results["record_list"] = records
    return JsonResponse(results)


def wechat_recharge(request):
    """ 微信充值 """
    amount = request.POST.get("amount")

    if not amount:
        return HttpResponseBadRequest()

    try:
        notify_url = "https://api.gouhuoapp.com/wallet/wechat_recharge_callback/"
        out_trade_no = random_str()
        wechat = WechatSDK()
        amount = get_related_amount(amount)
        appapi_params = wechat.create_order(body="充值",
                                            amount=amount,
                                            out_trade_no=out_trade_no,
                                            notify_url=notify_url,
                                            trade_type="APP")
        if appapi_params:
            WalletRecharge.objects.create(user_id=request.user.id,
                                          out_trade_no=out_trade_no,
                                          amount=amount)
            return JsonResponse({"return_code": "SUCCESS",
                                 "appapi_params": appapi_params,
                                 "out_trade_no": out_trade_no})
        return JsonResponse(error=WalletError.RECHARGE_FAIL)
    except:
        return JsonResponse(error=WalletError.RECHARGE_FAIL)


def wechat_recharge_callback(request):
    wechat = WechatSDK()
    xml = wechat.transfer_callback(request_body=request.body,
                                   func=WalletRecharge.recharge_callback)
    return HttpResponse(xml)


def client_recharge_callback(request):
    out_trade_no = request.POST.get("out_trade_no")
    is_success = WalletRecharge.recharge_callback(out_trade_no=out_trade_no)
    if is_success:
        return JsonResponse()
    return HttpResponseServerError()


def apply_withdrawal_to_wechat(request):
    code = request.POST.get("code")
    amount = request.POST.get("amount")

    wallet = Wallet.get(user_id=request.user.id)
    error = wallet.withdrawals_validate(amount)
    if error:
        return JsonResponse(error=error)

    try:
        amount = get_related_amount(amount=amount)
        wx_user_info = OAuth().get_user_info(code=code)
        if not wx_user_info:
            return JsonResponse(error=WalletError.WITHDRAWAL_FAIL)

        is_success = Withdrawals.apply(openid=wx_user_info["openid"],
                                       user_id=request.user.id,
                                       amount=amount)
        if is_success:
            return JsonResponse({"message": "提现成功, 系统正在进行结算, 您的提现金额将在24小时之内到账"})
    except Exception as e:
        if hasattr(e, "errcode"):
            if e.errcode in ["NOTENOUGH", "SYSTEMERROR", "AMOUNT_LIMIT"]:
                return JsonResponse(error={"return_code": e.result_code, "return_msg": e.errmsg})
        return JsonResponse(error=WalletError.WITHDRAWAL_FAIL)
    return HttpResponseServerError()


def wallet_record(request):
    page = int(request.POST.get("page", 1))

    record_list = WalletRecord.objects.filter(owner_id=request.user.id)

    results = {"record_list": [], "paginator": {}}
    record_list, paginator_dict = paginator(record_list, page, 30)
    records = []
    for record in record_list:
        user = User.get(record.owner_id)
        basic_info = user.basic_info()
        basic_info["record_msg"] = "%s - %s" % (user.nickname, record.type)
        basic_info["amount"] = Decimal(record.amount) // 100
        basic_info["type"] = record.type
        basic_info["category"] = record.category

        records.append(basic_info)

    results["paginator"] = paginator_dict
    results["record_list"] = records
    return JsonResponse(results)


def is_disable(request):
    if request.user.id == 45:
        return JsonResponse({"disable": True})
    return JsonResponse({"disable": False})
