from rongcloud import RongCloud as RC

from django.conf import settings


class RongCloud(object):

    def __init__(self):
        self.rongcloud = RC(settings.RONGCLOUD_APP_KEY, settings.RONGCLOUD_APP_SECRET)

    def publish_message(self, user_id, to_user_id, content):
        return self.rongcloud.Message.publishPrivate(
                    fromUserId=user_id,
                    toUserId=to_user_id,
                    objectName='IDA:InstMsg',
                    content=content)

    def create_group(self, user_id, group_id, group_name):
        self.rongcloud.Group.create(userId=user_id, groupId=group_id, groupName=group_name)
