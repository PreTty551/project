import os
import sys

from .user import User
from .friend import InviteFriend, Friend
from .contact import UserContact
import random


def init_data(user_id=None):
    for i in range(0, 50):
        User.objects.add_user(nickname="test%s" % i, mobile=18800000000 + i)

    for user in User.objects.all():
        for invite_user in User.objects.all():
            InviteFriend.add(user_id=user.id, invited_id=invite_user.id)

        for invite in InviteFriend.objects.all()[:25]:
            InviteFriend.agree(invite.user_id, invite.invited_id)


def init_data_to_user(user_id):
    for i in range(10, 20):
        UserContact.objects.create(user_id=user_id, name="test%s" % i, mobile=18800000000 + i)
        User.objects.add_user(nickname="test%s" % i, mobile=18800000000 + i)

    for j in range(11, 22):
        UserContact.objects.create(user_id=user_id, name="test%s" % j, mobile=18800000000 + j)

    for user in User.objects.exclude(id=user_id):
        InviteFriend.add(user_id=user.id, invited_id=user_id)


def init_gift():
    from gift.models import Gift
    Gift.objects.create(name="拍巴掌", amount=1, size="m", icon="", order=1)
    Gift.objects.create(name="比心心", amount=1, size="m", icon="", order=2)
    Gift.objects.create(name="甜甜圈", amount=1, size="m", icon="", order=3)
    Gift.objects.create(name="么么哒", amount=1, size="m", icon="", order=4)
    Gift.objects.create(name="666", amount=1, size="m", icon="", order=5)
    Gift.objects.create(name="鸡年大吉", amount=1, size="m", icon="", order=6)
    Gift.objects.create(name="熊宝宝", amount=1, size="m", icon="", order=7)
    Gift.objects.create(name="宝石皇冠", amount=1, size="l", icon="", order=8)



if __name__ =="__main__":
    init_data_to_user(1)
