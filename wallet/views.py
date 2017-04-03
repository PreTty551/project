from django.shortcuts import render

from back.models import out_trade_no, recharge


@login_required_404
def wechat_recharge(request):
    """ 微信充值 """
    amount = request.POST.get("amount")

    if not amount:
        return HttpResponseBadRequest()

    try:
        notify_url = "http://"
        out_trade_no = create_out_trade_no()
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
