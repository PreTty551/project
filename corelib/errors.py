# -*- coding: utf-8 -*-
from django.utils.translation import ugettext


class ErrorCodeField(int):
    def __new__(cls, error_code, return_msg=""):
        obj = int.__new__(cls, error_code)
        obj.return_code = error_code
        obj.return_msg = return_msg
        return obj


class ErrorCodeMetaClass(type):

    def __new__(cls, name, bases, namespace):
        code_message_map = {}
        for k, v in namespace.items():
            if getattr(v, '__class__', None) and isinstance(v, ErrorCodeField):
                if code_message_map.get(v):
                    raise ValueError("duplicated codde {0} {1}".format(k, v))
                code_message_map[v] = getattr(v, 'return_msg', "")
        namespace["CODE_MESSAGE_MAP"] = code_message_map
        return type.__new__(cls, name, bases, namespace)


class BaseError(metaclass=ErrorCodeMetaClass):
    CODE_MESSAGE_MAP = NotImplemented


class LoginError(BaseError):
    NOT_LOGIN = ErrorCodeField(10001, ugettext("未登录"))
    REQUEST_SMS_CODE = ErrorCodeField(10002, ugettext("请求验证码错误"))
    SMS_CODE_ERROR = ErrorCodeField(10003, ugettext("验证码不正确，请重新输入"))
    INVALID_NICKNAME = ErrorCodeField(10004, ugettext("昵称不可用"))
    INVALID_PHONE = ErrorCodeField(10005, ugettext("无效的手机号"))
    SEND_SMS_CODE = ErrorCodeField(10006, ugettext("发送验证码失败"))
    WX_LOGIN = ErrorCodeField(10007, ugettext("微信登录失败"))
    WB_LOGIN = ErrorCodeField(10008, ugettext("微博登录失败"))
    DISABLE_LOGIN = ErrorCodeField(10009, ugettext("账号已被封禁, 禁止登录"))
    BAND_ERROR = ErrorCodeField(10010, ugettext("绑定失败"))
    MOBILE_ALREADY_USED = ErrorCodeField(10011, ugettext("手机号已使用，请重新输入"))
