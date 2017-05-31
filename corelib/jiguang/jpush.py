# -*- coding: utf-8 -*-
import requests
import base64
import json
import jpush
import django_rq

from jpush import common

from django.conf import settings

from corelib.redis import redis
from user.consts import REDIS_NO_PUSH_IDS


class JPush(object):

    app_key = settings.JSMS_APP_KEY
    master_secret = settings.JSMS_MASTER_SECRET

    def __init__(self, user_id=""):
        self.client = jpush.JPush(self.app_key, self.master_secret)
        self.user_id = user_id

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
        return _

    def _get_valid_user_ids(self, user_ids):
        no_push_ids = redis.hkeys(REDIS_NO_PUSH_IDS % self.user_id)
        for no_push_id in no_push_ids:
            no_push_id = int(no_push_id.decode())
            if no_push_id in user_ids:
                user_ids.remove(no_push_id)

        return user_ids

    def push(self, user_ids, message, push_type=0, is_sound=False,
             sound=None, title="通知提醒", badge="", **kwargs):
        push = self.client.create_push()
        push.audience = jpush.audience({"alias": user_ids})
        ios = self._ios(is_sound=is_sound, sound=sound, push_type=push_type, badge=badge, **kwargs)
        android = self._android(title=title, push_type=push_type, **kwargs)
        push.notification = jpush.notification(alert=message, ios=ios, android=android)
        push.platform = "all"

        options = {"apns_production": True}
        apns_collapse_id = kwargs.get("apns_collapse_id")
        if apns_collapse_id:
            options["apns_collapse_id"] = apns_collapse_id

        push.options = options

        try:
            push.send()
        except common.Unauthorized:
            raise common.Unauthorized("Unauthorized")
        except common.APIConnectionException:
            raise common.APIConnectionException("conn error")
        except common.JPushFailure as e:
            # 没有满足条件的推送目标
            if e.error_code == 1011:
                return
            raise Exception(e.error)
        except Exception as e:
            raise e

    def async_push(self, user_ids, message, push_type=0, is_sound=False,
                   sound=None, title="通知提醒", badge="", is_valid_role=True, **kwargs):
        if is_valid_role:
            user_ids = self._get_valid_user_ids(user_ids=user_ids)

        if user_ids:
            queue = django_rq.get_queue('push')
            queue.enqueue(self.push, user_ids, message, push_type, is_sound, sound, title, badge, **kwargs)

    def async_batch_push(self, user_ids, message, push_type=0, is_sound=False,
                         sound=None, title="通知提醒", badge="", is_valid_role=True, **kwargs):
        if is_valid_role:
            user_ids = self._get_valid_user_ids(user_ids=user_ids)

        if user_ids:
            # query的限制是1000，所以一次发1000个人
            limit = 0
            offset = 1000
            receive_count = len(user_ids)
            loop_num = receive_count // offset
            if (receive_count % offset):
                loop_num += 1

            queue = django_rq.get_queue('push')
            for i in list(range(loop_num)):
                queue.enqueue(self.push, user_ids[limit: limit + offset], message, push_type, is_sound, sound, title, badge, **kwargs)
                limit += 1000
