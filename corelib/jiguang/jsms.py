# -*- coding: utf-8 -*-
import requests
import base64
import json
import jpush

from django.conf import settings
from corelib.redis import redis

JSMS_ERROR_CODES = {
    50000: u"请求成功",
    50009: u"抱歉, 同一手机号一天只能接收10条",
    50010: u"验证码无效",
    50011: u"验证码过期",
    50012: u"验证码已验证过"
}
MC_JSMS_MSG_ID_KEY = "jsms:mobile:%s:msg"


class JSMS(object):
    """极光的短信服务

       获取验证码:
          jsms = JSMS(mobile=xx)
          code = jsms.request_code()

       验证:
          jsms = JSMS(mobile=xx)
          is_valid, err_txt = jsms.valid(code=xx)
    """

    app_key = settings.JSMS_APP_KEY
    master_secret = settings.JSMS_MASTER_SECRET
    request_code_url = "https://api.sms.jpush.cn/v1/codes"
    valid_code_url = "https://api.sms.jpush.cn/v1/codes/%s/valid"
    request_voice_code_url = "https://api.sms.jpush.cn/v1/voice_codes"
    expire = 60 * 60

    def __init__(self, mobile, temp_id=10776):
        self.mobile = mobile
        self.temp_id = temp_id

    @property
    def _auth(self):
        auth = ("%s:%s" % (self.app_key, self.master_secret)).encode(encoding="utf-8")
        return base64.b64encode(auth).decode()

    def _send(self, url, **kwargs):
        headers = {"Content-Type": "application/json",
                   "Authorization": "Basic %s" % self._auth}
        return requests.post(url, headers=headers, data=json.dumps(kwargs)).json()

    @property
    def msg_id(self):
        msg_id = redis.get(MC_JSMS_MSG_ID_KEY % self.mobile)
        return msg_id.decode() or ""

    def request_code(self):
        res = self._send(url=self.request_code_url,
                         mobile=self.mobile,
                         temp_id=self.temp_id)

        if res.get("error"):
            error_message = self.error_message(res.get("error")["code"], u"请求验证码失败")
            return False, error_message

        msg_id = res.get("msg_id")
        if msg_id:
            redis.set(MC_JSMS_MSG_ID_KEY % self.mobile, msg_id, self.expire)

        return True, None

    def request_voice_code(self):
        res = self._send(url=self.request_voice_code_url,
                         mobile=self.mobile,
                         temp_id=self.temp_id,
                         ttl=600)
        if res.get("error"):
            error_message = self.error_message(res.get("error")["code"], u"请求验证码失败")
            return False, error_message

        msg_id = res.get("msg_id")
        if msg_id:
            redis.set(MC_JSMS_MSG_ID_KEY % self.mobile, msg_id, self.expire)

        return True, None

    def error_message(self, error_code, error_msg):
        return {int(error_code): JSMS_ERROR_CODES.get(int(error_code), error_msg)}

    def valid(self, code):
        valid_code_url = self.valid_code_url % self.msg_id
        res = self._send(url=valid_code_url, code=code)

        if res.get("error"):
            error_message = self.error_message(res.get("error")["code"], u"验证码错误")
            return res["is_valid"], error_message
        return res["is_valid"], None
