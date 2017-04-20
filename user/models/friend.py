# -*- coding: utf-8 -*-
import time
from django.db import models, transaction, IntegrityError

from corelib.utils import natural_time as time_format
from corelib.redis import redis

from user.models import User
from user.consts import UserEnum, MC_FRIEND_IDS_KEY, REDIS_MEMOS_KEY
from corelib.mc import hlcache


class InviteFriend(models.Model):
    user_id = models.IntegerField()
    invited_id = models.IntegerField()
    status = models.SmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('invited_id', 'user_id'))

    @classmethod
    def add(cls, user_id, invited_id):
        try:
            return cls.objects.create(user_id=user_id, invited_id=invited_id)
        except IntegrityError:
            pass

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
        return True if cls.objects.filter(user_id=friend_id, invited_id=user_id).first() else False

    @classmethod
    def get_invited_my_ids(cls, owner_id):
        return list(cls.objects.filter(invited_id=owner_id,
                                       status=0).values_list("user_id", flat=True))


class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    notify_switch = models.BooleanField(default=True)
    memo = models.CharField(max_length=100, default="")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user_id', 'friend_id'))

    @classmethod
    def is_friend(cls, owner_id, friend_id):
        friend_ids = cls.get_friend_ids(user_id=owner_id)
        return friend_id in friend_ids

    @classmethod
    @hlcache(MC_FRIEND_IDS_KEY % '{user_id}')
    def get_friend_ids(cls, user_id):
        return list(cls.objects.filter(user_id=user_id).values_list("friend_id", flat=True))

    @classmethod
    def who_is_friends(cls, owner_id, friend_ids):
        quertset = Friend.objects.filter(user_id=owner_id, friend_id__in=friend_ids)
        return list(quertset.values_list("friend_id", flat=True))

    @classmethod
    @transaction.atomic()
    def add(cls, user_id, friend_id):
        Friend.objects.create(user_id=user_id, friend_id=friend_id)
        Friend.objects.create(user_id=friend_id, friend_id=user_id)
        return True

    @classmethod
    @transaction.atomic()
    def delete_friend(cls, owner_id, friend_id):
        cls.objects.filter(user_id=owner_id, friend_id=friend_id).delete()
        cls.objects.filter(user_id=friend_id, friend_id=owner_id).delete()
        redis.hdel(MC_FRIEND_IDS_KEY % owner_id, friend_id)
        redis.hdel(MC_FRIEND_IDS_KEY % friend_id, owner_id)
        redis.hdel(REDIS_MEMOS_KEY % owner_id, friend_id)
        return True

    @classmethod
    def get_memo(cls, owner_id, friend_id):
        return redis.hget(REDIS_MEMOS_KEY % owner_id, friend_id)

    def update_memo(self, memo):
        self.memo = memo
        self.save()
        redis.hset(REDIS_MEMOS_KEY % self.user_id, self.user_id, memo)
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
        results = {"#": []}

        for friend in friends:
            if not friend:
                continue

            pinyin = friend.pinyin
            if pinyin[0].isalpha():
                ll = results.setdefault(pinyin[0].upper(), [])
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


def common_friend(user_id, to_user_id):
    user_ids = Friend.get_friend_ids(user_id)
    to_user_id = Friend.get_friend_ids(to_user_id)

    u_ids = set(user_ids) & set(to_user_id)
    return [User.get(uid).nickname for uid in u_ids if User.get(uid)]
