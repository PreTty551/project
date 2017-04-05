# -*- coding: utf-8 -*-
from django.db import models, transaction

from corelib.utils import natural_time as time_format

from user.models import User


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
        cls.objects.filter(user_id=user_id, invited_id=invited_id).update(status=1)
        Friend.add(user_id=user_id, friend_id=invited_id)

    @classmethod
    def ignore(cls, id):
        cls.objects.filter(id=id).update(status=2)

    @classmethod
    def count(cls, user_id):
        return cls.objects.filter(invited_id=user_id).count()

    @classmethod
    def get_add_friend_request_list(cls, user_id):
        return list(cls.objects.filter(friend_id=user_id, status=0).values_list("user_id", flat=True))


class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    notify_switch = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

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
    @transaction.atomic()
    def cancel(cls, user_id, friend_id):
        cls.objects.filter(user_id=user_id, friend_id=friend_id).delete()
        cls.objects.filter(user_id=friend_id, friend_id=user_id).delete()
        return True

    @classmethod
    def get_friend_ids(cls, user_id):
        return list(cls.objects.filter(user_id=user_id).values_list("friend_id", flat=True))

    @classmethod
    def is_invited_user(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=friend_id, friend_id=user_id).first() else False

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
        user = User.get(id=user_id)
        basic_info = user.basic_info()
        mutual_friend = [User.get(friend_id).nickname for friend_id in mutual_friend_ids]
        basic_info["mutual_friend"] = mutual_friend
        result.append(basic_info)
    return result
