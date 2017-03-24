# -*- coding: utf-8 -*-
import time

from wechatpy import WeChatClient
from wechatpy.oauth import WeChatOAuth

from django.conf import settings
from corelib.utils import random_str


class JSSDK(object):

    @classmethod
    def config(cls, url, appid=None, secret=None):
        if appid is None:
            appid = settings.WECHAT_APP_ID
        if secret is None:
            secret = settings.WECHAT_APP_SECRET

        client = WeChatClient(appid, secret)
        ticket = client.jsapi.get_jsapi_ticket()
        timestamp = int(time.time())
        nonce_str = random_str(num=6)
        signature = client.jsapi.get_jsapi_signature(noncestr=nonce_str,
                                                     ticket=ticket,
                                                     timestamp=timestamp,
                                                     url=url)
        return {
            "appId": appid,
            "timestamp": timestamp,
            "nonceStr": nonce_str,
            "signature": signature,
            "link": url
        }


class OAuth(object):

    @classmethod
    def get_user_info(cls, code):
        try:
            wechat = WeChatOAuth(settings.WECHAT_OPEN_APP_ID, settings.WECHAT_OPEN_APP_SECRET, '')
            res = wechat.fetch_access_token(code=code)
            return wechat.get_user_info(openid=res["openid"], access_token=res["access_token"])
        except:
            return
