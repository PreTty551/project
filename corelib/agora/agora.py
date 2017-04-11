# -*- coding: utf-8 -*-

import time
import hashlib
import random
import requests
import hmac
import json
import base64

from datetime import timedelta
from datetime import datetime

from django.conf import settings

from .dynamickey5 import generateMediaChannelKey


class Agora(object):

    def __init__(self, user_id):
        self.app_id = settings.AGORA_KEY
        self.app_secret = settings.AGORA_SECRET
        self.user_id = user_id
        self.url = "http://api.sig.agora.io/api1"

    def get_channel_madia_key(self, channel_name):
        return generateMediaChannelKey(self.app_id,
                                       self.app_secret,
                                       channel_name,
                                       int(time.time()),
                                       random.randint(100000000, 1000000000),
                                       self.user_id,
                                       0).decode()

    def get_signaling_key(self):
        return self._create_signaling_token()

    def _create_signaling_token(self):
        """token生成规则
           "1:appId:expiredTime:md5(account + appId + appCertificate + expiredTime)"
        """
        t = datetime.now() + timedelta(minutes=30)
        expired_time = int(time.mktime(t.timetuple()))
        _ = "%s%s%s%s" % (self.user_id, self.app_id, self.app_secret, expired_time)
        md5 = hashlib.md5()
        md5.update(_.encode("utf8"))
        md5_str = md5.hexdigest()
        return "1:%s:%s:%s" % (self.app_id, expired_time, md5_str)

    def _call(self, func, **kargs):
        req = {
            "_appId": self.app_id,
            "_callid": self.unique_channel_id,
            "_timestamp": datetime.now().isoformat(),
            "_function": func,
        }
        req.update(kargs)

        keys = req.keys()
        keys = sorted(keys)
        signstr = ''.join(k + req[k] for k in keys)
        signstr = signstr.lower()
        sign = hmac.new(self.app_secret.encode(), signstr.encode(), hashlib.sha1).hexdigest()
        req['_sign'] = sign

        resp = requests.post(self.url, data=json.dumps(req))
        return resp.json()

    @property
    def unique_channel_id(self):
        return "%s%s" % (int(time.time()), self.user_id)

    def send_cannel_msg(self, channel_id, **kwargs):
        msg = base64.b64encode(json.dumps(kwargs).encode())
        _ = {"name": str(channel_id), "msg": msg.decode()}
        self._call("channel_sendmsg", account=str(self.user_id), kargs=json.dumps(_))

    def subscribe_online(self):
        self._call("subscribe_online", url="https://gouhuoapp.com/api/v2/agora/user_online_callback/")
