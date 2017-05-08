# -*- coding: utf-8 -*-
from django.conf import settings

from wechatpy.pay import WeChatPay

from corelib.utils import dict_to_xml, random_str


class WechatSDK(object):

    def __init__(self, mch_id=None):
        self.wechatpay = self._wechatpay()

    def _wechatpay(self, mch_id=None):
        """ 以后如果涉及多个商户, 利用mch_id做初始化 """
        return WeChatPay(
            appid=settings.WECHAT_OPEN_APP_ID,
            api_key=settings.WECHAT_OPEN_MCH_KEY,
            mch_id=settings.WECHAT_OPEN_MCH_ID,
            mch_cert=settings.WECHAT_OPEN_SSLCERT_PATH,
            mch_key=settings.WECHAT_OPEN_SSLKEY_PATH)

    def create_order(self, body, amount, out_trade_no, notify_url, trade_type="APP"):
        wechat_order = self.wechatpay.order.create(
                                            body=body,
                                            total_fee=str(amount),
                                            out_trade_no=out_trade_no,
                                            notify_url=notify_url,
                                            trade_type=trade_type)

        appapi_params = self.wechatpay.order.get_appapi_params(prepay_id=wechat_order["prepay_id"])
        return appapi_params

    def transfer_callback(self, request_body, func):
        result = self.wechatpay.parse_payment_result(xml=request_body)
        if result["return_code"] == "SUCCESS":
            res = {"return_code": "SUCCESS"}
            try:
                func(out_trade_no=result["out_trade_no"])
                return dict_to_xml(res)
            except:
                res["return_msg"] = "ERROR"
                return dict_to_xml(res)

        res["return_msg"] = "ERROR"
        return dict_to_xml(res)

    def enterprise_pay(self, openid, amount, desc, check_name="NO_CHECK"):
        recode = self.wechatpay.transfer.transfer(user_id=openid,
                                                  amount=int(amount),
                                                  desc=desc,
                                                  check_name=check_name)

        if recode["return_code"] == "SUCCESS" and recode["result_code"] == "SUCCESS":
            return True, None
        return False, recode


def create_out_trade_no(num=10):
    """生成随机的订单号"""
    return random_str(num=10)
