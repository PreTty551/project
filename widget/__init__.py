from django.db import models

from user.models import Friend
from live.models import Channel


class Widget(object):

    def list(cls, user_id):
        pass


class FriendListWidget(Widget):

    def list(cls, user_id):
        return Friend.get_friends_order_by_date(user_id=user_id)


class ChannelListWidget(Widget):

    def list(cls, user_id):
        return Channel.get_friend_channels(user_id=user_id)


class ChannelInnerListWidget(Widget):

    def list(cls, user_id):
        return Channel.get_friend_channels(user_id=user_id, channel_type=ChannelType.normal.value)
