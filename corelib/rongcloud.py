import hashlib

from rongcloud import RongCloud as RC

from django.conf import settings


class RongCloud(object):

    def __init__(self):
        self.rongcloud = RC(settings.RONGCLOUD_APP_KEY, settings.RONGCLOUD_APP_SECRET)

    def valid_signature(self, nonce, timestamp, signature):
        _signature = hashlib.sha1((settings.RONGCLOUD_APP_SECRET + nonce + timestamp).encode('utf-8')).hexdigest()
        return signature == _signature

    def _send(self, user_id, to_user_id, content, object_name):
        return self.rongcloud.Message.publishPrivate(
                    fromUserId=user_id,
                    toUserId=to_user_id,
                    objectName=object_name,
                    content=content,
                    isPersisted=16)

    def send_inner_message(self, user_id, to_user_id, content):
        return self._send(user_id=user_id,
                          to_user_id=to_user_id,
                          object_name='IDA:InstMsg',
                          content=content)

    def send_hide_message(self, user_id, to_user_id, content):
        return self._send(user_id=user_id,
                          to_user_id=to_user_id,
                          object_name='IDA:InnerMsg',
                          content=content)

    def create_group(self, user_id, group_id, group_name):
        self.rongcloud.Group.create(userId=user_id, groupId=group_id, groupName=group_name)
