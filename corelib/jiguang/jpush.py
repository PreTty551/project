# -*- coding: utf-8 -*-
import requests
import base64
import json
import jpush

from django.conf import settings
from corelib.redis import redis


class JPush(object):

    app_key = settings.JSMS_APP_KEY
    master_secret = settings.JSMS_MASTER_SECRET

    def __init__(self):
        self.client = jpush.JPush(self.app_key, self.master_secret)
        self.client.set_logging("DEBUG")

    def _ios(self, is_sound, sound, push_type, **kwargs):
        _ = {
            "extras": {
                "type": push_type,
                **kwargs
            }
        }
        if is_sound and sound:
            _["sound"] = sound
        return _

    def _android(self, title, push_type, **kwargs):
        _ = {
            "title": title,
            "extras": {
                "type": push_type,
                **kwargs
            }
        }

    def push(self, user_ids, message, push_type=0, is_sound=False,
             sound=None, title="通知提醒", **kwargs):

        push = self.client.create_push()
        push.audience = jpush.audience({"alias": user_ids})
        ios = self._ios(is_sound=is_sound, sound=sound, push_type=push_type, **kwargs)
        android = self._android(title=title, push_type=push_type, **kwargs)
        push.notification = jpush.notification(alert=message, ios=ios, android=android)
        push.options = {"apns_production": False}
        push.platform = ["android", "ios"]
        push.send()
