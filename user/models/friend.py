# -*- coding: utf-8 -*-
from django.db import models, transaction

from corelib.utils import natural_time as time_format

from user.models import User
from user.consts import UserEnum


class InviteFriend(models.Model):
    user_id = models.IntegerField()
    invited_id = models.IntegerField()
    status = models.SmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def add(cls, user_id, invited_id):
        return cls.objects.create(user_id=user_id, invited_id=invited_id)

    @classmethod
    def agree(cls, user_id, invited_id):
        cls.objects.filter(user_id=invited_id, invited_id=user_id).update(status=1)
        return Friend.add(user_id=invited_id, friend_id=user_id)

    @classmethod
    def ignore(cls, id):
        cls.objects.filter(id=id).update(status=2)

    @classmethod
    def count(cls, user_id):
        return cls.objects.filter(invited_id=user_id).count()

    @classmethod
    def is_invited_user(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=friend_id, friend_id=user_id).first() else False

    @classmethod
    def get_invite_friend_ids(cls, user_id, user_ranges=[]):
        if not user_ranges:
            return list(cls.objects.filter(invited_id=user_id,
                                           status=0).values_list("user_id", flat=True))
        return list(cls.objects.filter(invited_id=user_id,
                                       status=0,
                                       user_id__in=user_ranges).values_list("user_id", flat=True))

    @classmethod
    def get_invite_friends(cls, user_id, user_ranges=[]):
        invite_friend_ids = cls.get_invite_friend_ids(user_id=user_id,
                                                      user_ranges=user_ranges)

        results = []
        for friend_id in invite_friend_ids:
            user = User.get(id=friend_id)
            if not user:
                continue

            basic_info = user.basic_info()
            basic_info["user_relation"] = UserEnum.be_invite.value
            results.append(basic_info)

        return results


class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    notify_switch = models.BooleanField(default=True)
    memo = models.CharField(max_length=100, default="")
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, friend_id):
        return cls.objects.filter(id=friend_id).first()

    @classmethod
    @transaction.atomic()
    def add(cls, user_id, friend_id):
        Friend.objects.create(user_id=user_id, friend_id=friend_id)
        Friend.objects.create(user_id=friend_id, friend_id=user_id)
        return True

    @property
    def localtime(self):
        return timezone.localtime(self.date)

    @property
    def natural_time(self):
        return time_format(self.localtime)

    @classmethod
    def count(cls, user_id):
        return cls.objects.filter(user_id=user_id).count()

    @classmethod
    @transaction.atomic()
    def cancel(cls, user_id, friend_id):
        cls.objects.filter(user_id=user_id, friend_id=friend_id).delete()
        cls.objects.filter(user_id=friend_id, friend_id=user_id).delete()
        return True

    @classmethod
    def get_friend_ids(cls, user_id):
        return list(cls.objects.filter(user_id=user_id).values_list("friend_id", flat=True))

    @classmethod
    def is_friend(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=user_id, friend_id=friend_id).first() else False

    @classmethod
    def get_friends(cls, user_id):
        friend_ids = cls.objects.filter(user_id=user_id).values_list("friend_id", flat=True)
        firends = []
        for friend_id in friend_ids:
            user = User.get(id=friend_id)
            firends.append(user)

        return firends

    @classmethod
    def get_friends_order_by_pinyin(cls, user_id):
        friends = cls.get_friends(user_id=user_id)
        results = {}

        for friend in friends:
            if not friend:
                continue

            pinyin = friend.pinyin
            if pinyin[0].isalpha():
                ll = results.setdefault(pinyin[0], [])
                ll.append(friend.basic_info())
            else:
                results["#"].append(friend.basic_info())

        return results

    def to_dict(self):
        user = User.get(self.user_id)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nickname": user.nickname,
            "status": self.status,
        }


def two_degree_relation(user_id):
    friend_ids = list(Friend.objects.filter(user_id=user_id)
                                    .values_list("friend_id", flat=True))
    second_friend_list = list(Friend.objects.filter(user_id__in=friend_ids)
                                            .exclude(friend_id=user_id)
                                            .values_list("user_id", "friend_id"))

    obj = []
    for second_friend in second_friend_list:
        obj.append((second_friend[0], second_friend[1]))

    _dict = {}
    for uid, fid in obj:
        _ = _dict.setdefault(fid, [])
        _.append(uid)

    result = []
    for user_id, mutual_friend_ids in _dict.items():
        if len(mutual_friend_ids) < 2:
            continue

        user = User.get(id=user_id)
        if not user:
            continue

        basic_info = user.basic_info()
        mutual_friend = [User.get(friend_id).nickname for friend_id in mutual_friend_ids]
        basic_info["mutual_friend"] = mutual_friend
        result.append(basic_info)
    return result
