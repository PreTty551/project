from django.db import models

from user.models import Friend
from live.models import Channel
from live.consts import ChannelType


class Widget(object):

    @classmethod
    def list(cls, user_id):
        pass


class FriendListWidget(Widget):

    @classmethod
    def list(cls, user_id):
        return Friend.get_friends_order_by_date(user_id=user_id)


class ChannelListWidget(Widget):

    @classmethod
    def list(cls, user_id):
        return Channel.get_friend_channels(user_id=user_id)


class ChannelInnerListWidget(Widget):

    @classmethod
    def list(cls, user_id):
        return Channel.get_friend_channels(user_id=user_id)
