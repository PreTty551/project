# -*- coding: utf-8 -*-

import json
import requests
import django_rq

from django.conf import settings


class LeanCloud(object):
    headers = {
        'X-AVOSCloud-Application-Id': settings.AVOS_APPLICATION_ID,
        'X-AVOSCloud-Application-Key': settings.AVOS_APPLICATION_KEY,
        'Content-Type': 'application/json',
    }
    leancloud_url = 'https://api.leancloud.cn/1.1/'

    @classmethod
    def post(cls, apiurl, data):
        return requests.post(
                '%s%s' % (cls.leancloud_url, apiurl), data=json.dumps(data), headers=cls.headers, timeout=5)

    @classmethod
    def push(cls, receive_id, message):
        apiurl = "push"
        data = {
            "prod": "prod",
            "where": {
                "userId": int(receive_id),
            },
            "data": {
                "ios": {
                    "alert": message,
                    "badge": "Increment",
                    "sound": "",
                },
                "android": {
                    "alert": message,
                    "title": u"消息提醒",
                    "badge": "Increment",
                }
            }
        }
        requests.post('%s%s' % (cls.leancloud_url, apiurl), data=json.dumps(data),
                      headers=cls.headers, timeout=5)

    @classmethod
    def _post(cls, url, data, headers):
        requests.post(url, data=data, headers=headers, timeout=5)

    @classmethod
    def async_push(cls, receive_id, message, msg_type=0, channel_id=0):
        apiurl = "push"
        data = {
            "prod": "prod",
            "where": {
                "userId": int(receive_id),
            },
            "data": {
                "ios": {
                    "alert": message,
                    "sound": "",
                },
                "android": {
                    "alert": message,
                    "title": u"消息提醒",
                },
                "type": msg_type,
            }
        }
        if msg_type == 0:
            data["data"]["ios"]["badge"] = "Increment"
            data["data"]["android"]["badge"] = "Increment"

        if msg_type == 8:
            data["data"]["channel_id"] = channel_id
            # data["data"]["ios"]["sound"] = "push.caf"

        queue = django_rq.get_queue('high')
        queue.enqueue(_post, url='%s%s' % (cls.leancloud_url, apiurl), data=json.dumps(data), headers=cls.headers)

    @classmethod
    def async_batch_push(cls, receive_ids, message, msg_type=0):
        def _(receive_ids):
            apiurl = "push"
            data = {
                "prod": "prod",
                "where": {
                    "userId": {"$in": receive_ids},
                },
                "data": {
                    "ios": {
                        "alert": message,
                        "sound": "",
                    },
                    "android": {
                        "alert": message,
                        "title": u"消息提醒",
                    },
                    "type": msg_type,
                }
            }

            if msg_type == 0:
                data["data"]["ios"]["badge"] = "Increment"
                data["data"]["android"]["badge"] = "Increment"

            queue = django_rq.get_queue('high')
            queue.enqueue(_post, url='%s%s' % (cls.leancloud_url, apiurl), data=json.dumps(data), headers=cls.headers)

        # query的限制是1000，所以一次发1000个人
        limit = 0
        offset = 1000
        receive_count = len(receive_ids)
        loop_num = receive_count / offset
        if (receive_count % offset):
            loop_num += 1

        for i in range(loop_num):
            _(receive_ids[limit: limit + offset])
            limit += 1000

    @classmethod
    def register(cls, device_token, user_id):
        apiurl = "installations"
        data = {
            "deviceType": "ios",
            "deviceToken": device_token,
            "userId": user_id,
            "timeZone": 'Asia/Shanghai',
            "badge": 0,
            "channels": [
                "public", "protected", "private"
            ]
        }
        requests.post('%s%s' % (cls.leancloud_url, apiurl), data=json.dumps(data),
                      headers=cls.headers, timeout=5)

    def clear_badge(cls, device_token, badge=0):
        if device_token:
            apiurl = "installations"
            data = {
                "deviceType": "ios",
                "deviceToken": device_token,
                "userId": None,
                "timeZone": 'Asia/Shanghai',
                "badge": badge,
            }
            requests.post('%s%s' % (cls.leancloud_url, apiurl), data=json.dumps(data),
                          headers=cls.headers, timeout=5)

def _post(url, data, headers):
    requests.post(url, data=data, headers=headers, timeout=5)
