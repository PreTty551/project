import json
from enum import Enum
from corelib.rongcloud import RongCloud


LocalPushType = Enum("LocalPushType", ("add_friend", "agree_friend", "party", "invite_party", "private_party", "poke"))


class LocalPush(object):

    def __init__(self):
        self.client = RongCloud()

    def _push(self, user_id, to_user_id, message, push_type):
        _ = {
            "type": push_type,
            "data": {
                "message": message
            }
        }
        return self.client.publish_message(user_id=user_id,
                                           to_user_id=to_user_id,
                                           content=json.dumps(_))

    def agree_friend(self, user_id, to_user_id, message):
        return self._push(user_id=user_id,
                          to_user_id=to_user_id,
                          message=message,
                          push_type=LocalPushType.agree_friend.value)

    def add_friend(self, user_id, to_user_id, message):
        return self._push(user_id=user_id,
                          to_user_id=to_user_id,
                          message=message,
                          push_type=LocalPushType.add_friend.value)

    def party(self, user_id, to_user_id, message):
        return self._push(user_id=user_id,
                          to_user_id=to_user_id,
                          message=message,
                          push_type=LocalPushType.party.value)

    def invite_party(self, user_id, to_user_id, message):
        return self._push(user_id=user_id,
                          to_user_id=to_user_id,
                          message=message,
                          push_type=LocalPushType.invite_party.value)

    def private_party(self, user_id, to_user_id, message):
        return self._push(user_id=user_id,
                          to_user_id=to_user_id,
                          message=message,
                          push_type=LocalPushType.private_party.value)

    def poke(self, user_id, to_user_id, message):
        return self._push(user_id=user_id,
                          to_user_id=to_user_id,
                          message=message,
                          push_type=LocalPushType.poke.value)
