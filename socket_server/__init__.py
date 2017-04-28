import json
import time

from enum import Enum, unique
from corelib.rongcloud import RongCloud
from django.conf import settings

@unique
class PopBoxType(Enum):
    message = 0
    invite_friend = 1


@unique
class MessageType(Enum):
    not_hit = 0
    hit = 1


@unique
class EventType(Enum):
    refresh_home = 0
    refresh_inner_home = 1
    refresh_public = 2
    refresh_private = 3
    refresh_friend = 4


class SocketServer(object):
    """ 基于融云的socket来实现的功能 """

    def __init__(self):
        self.client = RongCloud()

    def _send_message(self, user_id, to_user_id, box_type, msg_type, message, **kwargs):
        """
        外层type对应客户端的弹出消息样式
        data里的type是message的type, 用来控制同一种消息处理逻辑不同的情况
        例如：
            box_type=0, msg_type=1
            意思是: 客户端弹出app内部的push，并且点击跳转到直播页

            box_type=0, msg_type=0
            意思是: 客户端弹出app内部的push，但无法点击
        """
        data = {
            "type": box_type,
            "data": {
                "type": msg_type,
                "message": message,
                **kwargs
            },
            "time": int(time.time() * 1000)
        }
        return self.client.send_inner_message(user_id=user_id,
                                              to_user_id=to_user_id,
                                              content=json.dumps(data))

    def _send_event(self, user_id, to_user_id, event_type, message, **kwargs):
        data = {
            "type": event_type,
            "data": {
                "message": message,
                **kwargs
            },
            "time": int(time.time() * 1000)
        }
        return self.client.send_hide_message(user_id=user_id,
                                             to_user_id=to_user_id,
                                             content=json.dumps(data))

    def invite_friend(self, user_id, to_user_id, message, **kwargs):
        return self._send_message(user_id=user_id,
                                  to_user_id=to_user_id,
                                  box_type=PopBoxType.invite_friend.value,
                                  msg_type=MessageType.hit.value,
                                  message=message,
                                  **kwargs)

    def agree_friend(self, user_id, to_user_id, message):
        return self._send_message(user_id=user_id,
                                  to_user_id=to_user_id,
                                  box_type=PopBoxType.message.value,
                                  msg_type=MessageType.not_hit.value,
                                  message=message,
                                  icon_url="%s/pa/friend.png" % settings.AVATAR_BASE_URL)

    def invite_party_in_live(self, user_id, to_user_id, message, channel_id):
        return self._send_message(user_id=user_id,
                                  to_user_id=to_user_id,
                                  box_type=PopBoxType.message.value,
                                  msg_type=MessageType.not_hit.value,
                                  message=message,
                                  channel_id=channel_id,
                                  icon_url="%s/pa/party.png" % settings.AVATAR_BASE_URL)

    def invite_party_out_live(self, user_id, to_user_id, message):
        return self._send_message(user_id=user_id,
                                  to_user_id=to_user_id,
                                  box_type=PopBoxType.message.value,
                                  msg_type=MessageType.hit.value,
                                  message=message,
                                  channel_id=0,
                                  icon_url="%s/pa/party.png" % settings.AVATAR_BASE_URL)

    def refresh(self, user_id, to_user_id, message, event_type):
        return self._send_event(user_id=user_id,
                                to_user_id=to_user_id,
                                event_type=event_type,
                                message=message)
