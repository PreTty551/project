# -*- coding: utf-8 -*-
import requests
import base64
import json
import jpush
import django_rq

from django.conf import settings
from corelib.redis import redis


class JPush(object):

    app_key = settings.JSMS_APP_KEY
    master_secret = settings.JSMS_MASTER_SECRET

    def __init__(self):
        self.client = jpush.JPush(self.app_key, self.master_secret)
        self.client.set_logging("DEBUG")

    def _ios(self, is_sound, sound, push_type, badge, **kwargs):
        _ = {
            "extras": {
                "type": push_type,
                **kwargs
            }
        }
        if is_sound and sound:
            _["sound"] = sound
        if badge:
            _["badge"] = badge
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
             sound=None, title="通知提醒", badge="", **kwargs):

        push = self.client.create_push()
        push.audience = jpush.audience({"alias": user_ids})
        ios = self._ios(is_sound=is_sound, sound=sound, push_type=push_type, badge=badge, **kwargs)
        android = self._android(title=title, push_type=push_type, **kwargs)
        push.notification = jpush.notification(alert=message, ios=ios, android=android)
        push.options = {"apns_production": True}
        push.platform = ["android", "ios"]
        push.send()

    def async_push(self, user_ids, message, push_type=0, is_sound=False,
                   sound=None, title="通知提醒", badge="", **kwargs):
        queue = django_rq.get_queue('high')
        queue.enqueue(self.push, user_ids, message, push_type, is_sound, sound, title, badge, **kwargs)

    def async_batch_push(self, user_ids, message, push_type=0, is_sound=False,
                         sound=None, title="通知提醒", badge="", **kwargs):
        # query的限制是1000，所以一次发1000个人
        limit = 0
        offset = 1000
        receive_count = len(user_ids)
        loop_num = receive_count // offset
        if (receive_count % offset):
            loop_num += 1

        queue = django_rq.get_queue('high')
        for i in list(range(loop_num)):
            queue.enqueue(self.push, user_ids[limit: limit + offset], message, push_type, is_sound, sound, title, badge, **kwargs)
            limit += 1000
