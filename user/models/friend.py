# -*- coding: utf-8 -*-
import time
import datetime

from django.db import models, transaction, IntegrityError
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from corelib.utils import natural_time as time_format
from corelib.redis import redis
from corelib.mc import hlcache, cache

from user.models import User
from user.consts import UserEnum, MC_FRIEND_IDS_KEY, REDIS_MEMOS_KEY, REDIS_PUSH_KEY, REDIS_INVISIBLE_KEY, MC_FRIEND_LIST
from live.consts import MC_PAING


class ChannelAddFriendLog(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    channel_type = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)


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
            cls.objects.create(user_id=user_id, invited_id=invited_id)
        except IntegrityError:
            pass
        return True

    @classmethod
    def agree(cls, user_id, invited_id):
        cls.objects.filter(user_id=invited_id, invited_id=user_id).update(status=1)
        return Friend.add(user_id=invited_id, friend_id=user_id)

    @classmethod
    def ignore(cls, id):
        cls.objects.filter(id=id).update(status=2)

    @classmethod
    def count(cls, user_id):
        return cls.objects.filter(invited_id=user_id, status=0).count()

    @classmethod
    def is_invite_user(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=friend_id, invited_id=user_id, status=0).first() else False

    @classmethod
    def is_invited_user(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=user_id, invited_id=friend_id, status=0).first() else False

    @classmethod
    def get_invited_my_ids(cls, owner_id):
        return list(cls.objects.filter(invited_id=owner_id,
                                       status=0).values_list("user_id", flat=True))

    @classmethod
    def get_my_invited_ids(cls, owner_id):
        return list(cls.objects.filter(user_id=owner_id,
                                       status=0).values_list("invited_id", flat=True))


class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    invisible = models.BooleanField(default=False)
    push = models.BooleanField(default=True)
    memo = models.CharField(max_length=100, default="")
    is_hint = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default=timezone.now)

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

    # @cache(MC_FRIEND_LIST % '{user_id}')
    @classmethod
    def get_friends_order_by_date(cls, user_id):
        friends = cls.objects.filter(user_id=user_id).order_by("update_date")
        return [friend.to_dict() for friend in friends]

    @classmethod
    def who_is_friends(cls, owner_id, friend_ids):
        quertset = Friend.objects.filter(user_id=owner_id, friend_id__in=friend_ids)
        return list(quertset.values_list("friend_id", flat=True))

    @classmethod
    @transaction.atomic()
    def add(cls, user_id, friend_id):
        Friend.objects.create(user_id=user_id, friend_id=friend_id)
        Friend.objects.create(user_id=friend_id, friend_id=user_id)
        InviteFriend.objects.filter(user_id=user_id, invited_id=friend_id).delete()
        InviteFriend.objects.filter(user_id=friend_id, invited_id=user_id).delete()
        return True

    @classmethod
    @transaction.atomic()
    def delete_friend(cls, owner_id, friend_id):
        cls.objects.filter(user_id=owner_id, friend_id=friend_id).delete()
        cls.objects.filter(user_id=friend_id, friend_id=owner_id).delete()
        return True

    def clear_mc(self):
        redis.delete(MC_FRIEND_LIST % self.user_id)
        redis.hdel(MC_FRIEND_IDS_KEY % self.user_id)
        redis.hdel(REDIS_MEMOS_KEY % self.user_id, self.friend_id)

    @classmethod
    def get_memo(cls, owner_id, friend_id):
        return redis.hget(REDIS_MEMOS_KEY % owner_id, friend_id)

    def update_memo(self, memo):
        self.memo = memo
        self.save()
        redis.hset(REDIS_MEMOS_KEY % self.user_id, self.user_id, memo)
        return True

    def update_invisible(self, is_invisible):
        self.invisible = is_invisible
        self.save()
        redis.hset(REDIS_INVISIBLE_KEY % self.user_id, self.user_id, is_invisible)
        return True

    def update_push(self, is_push):
        self.push = is_push
        self.save()
        redis.hset(REDIS_PUSH_KEY % self.user_id, self.user_id, is_push)
        return True

    @classmethod
    def is_invisible(cls, owner_id, user_id):
        is_invisible = redis.hget(REDIS_INVISIBLE_KEY % owner_id, user_id)
        if is_invisible is not None:
            return True if is_invisible else False
        return False

    @classmethod
    def is_push(cls, owner_id, user_id):
        is_push = redis.hget(REDIS_PUSH_KEY % owner_id, user_id)
        if is_push is not None:
            return True if is_push else False
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
    def get_friends_order_by_pinyin(cls, user_id):
        friend_list = cls.get_friends_order_by_date(user_id=user_id)
        results = {"#": []}

        for friend_dict in friend_list:
            pinyin = friend_dict["pinyin"]
            if pinyin[0].isalpha():
                ll = results.setdefault(pinyin[0].upper(), [])
                ll.append(friend_dict)
            else:
                results["#"].append(friend_dict)

        return results

    def to_dict(self):
        user = User.get(self.friend_id)
        basic_info = user.basic_info()
        basic_info["is_hint"] = self.is_hint
        basic_info["user_relation"] = UserEnum.friend.value
        basic_info["dynamic"] = friend_dynamic(self.user_id)
        basic_info["pinyin"] = user.pinyin
        return basic_info


def friend_dynamic(user_id):
    user = User.get(user_id)
    last_pa_time = user.last_pa_time
    if not last_pa_time:
        return

    try:
        dt = datetime.datetime.fromtimestamp(float(last_pa_time))
    except:
        return ""

    d = time_format(timezone.localtime(dt))
    if redis.get(MC_PAING % user_id):
        return "正在开PA"
    elif (datetime.datetime.now() - dt).seconds < 600:
        return "刚刚离开房间"
    elif (datetime.datetime.now() - dt).days < 4:
        return "%s开过PA" % d
    elif (datetime.datetime.now() - dt).days < 30:
        return "%s见过TA" % d


def common_friend(user_id, to_user_id):
    user_ids = Friend.get_friend_ids(user_id)
    to_user_id = Friend.get_friend_ids(to_user_id)

    u_ids = set(user_ids) & set(to_user_id)
    return [User.get(uid).nickname for uid in u_ids if User.get(uid)]


@receiver(post_save, sender=Friend)
def add_friend_after(sender, created, instance, **kwargs):
    if created:
        instance.clear_mc()


@receiver(post_delete, sender=Friend)
def del_friend_after(sender, instance, **kwargs):
    instance.clear_mc()
