from django.shortcuts import render
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.http import JsonResponse
from corelib.wechat import WechatSDK
from corelib.utils import random_str
from wallet.models import WalletRecharge, get_related_amount


@login_required_404
def wechat_recharge(request):
    """ 微信充值 """
    amount = request.POST.get("amount")

    if not amount:
        return HttpResponseBadRequest()

    try:
        notify_url = "http://api.gouhuoapp.com/"
        out_trade_no = random_str()
        wechat = WechatSDK()
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
        return JsonResponse({"return_code": "FAIL", "return_msg": u"充值失败"})
    except:
        return JsonResponse({"return_code": "FAIL", "return_msg": u"充值失败"})


def wechat_recharge_callback(request):
    wechat = WechatSDK()
    wechat.transfer_callback(request_body=request.body,
                             func=WalletRecharge.recharge_callback)


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
            return JsonResponse(error=WalletError.WITHDRAWAL_SUCCESS)
    except Exception as e:
        if hasattr(e, "errcode"):
            if e.errcode in ["NOTENOUGH", "SYSTEMERROR", "AMOUNT_LIMIT"]:
                return JsonResponse(error={"return_code": e.result_code, "return_msg": e.errmsg})
        return JsonResponse(error=WalletError.WITHDRAWAL_FAIL)
    return HttpResponseServerError()
