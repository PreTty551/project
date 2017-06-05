# -*- coding: utf-8 -*-
import time
import datetime
import pytz
import collections

from django.db import models, transaction, IntegrityError
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from corelib.utils import natural_time as time_format
from corelib.redis import redis
from corelib.mc import hlcache, cache

from user.models import User
from user.consts import UserEnum, MC_FRIEND_IDS_KEY, REDIS_MEMOS_KEY, REDIS_NO_PUSH_IDS, \
                        MC_INVITE_MY_FRIEND_IDS, MC_MY_INVITE_FRIEND_IDS, \
                        MC_INVITE_FRIEND_COUNT


class ChannelAddFriendLog(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField()
    channel_type = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "channel_add_friend_log"


class InviteFriend(models.Model):
    user_id = models.IntegerField()
    invited_id = models.IntegerField(db_index=True)
    status = models.SmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('invited_id', 'user_id'))

    @classmethod
    def add(cls, user_id, invited_id):
        invite = cls.objects.filter(user_id=invited_id, invited_id=user_id, status=0).first()
        if not invite:
            invite = cls.objects.filter(user_id=user_id, invited_id=invited_id).first()
            if invite:
                invite.status = 0
                invite.save()
            else:
                cls.objects.create(user_id=user_id, invited_id=invited_id)
        else:
            cls.objects.create(user_id=user_id, invited_id=invited_id)
        return True

    @classmethod
    def agree(cls, user_id, invited_id):
        invite = cls.objects.filter(user_id=invited_id, invited_id=user_id).first()
        if invite:
            invite.status = 1
            invite.save()
        return Friend.add(user_id=invited_id, friend_id=user_id)

    @classmethod
    def ignore(cls, id):
        cls.objects.filter(id=id).update(status=2)

    @classmethod
    # @cache(MC_INVITE_FRIEND_COUNT % '{user_id}')
    def count(cls, user_id, ignore_user_ids=[]):
        queryset = cls.objects.filter(invited_id=user_id, status=0)
        if ignore_user_ids:
            queryset = queryset.exclude(user_id__in=ignore_user_ids)
        return queryset.count()

    @classmethod
    def is_invite_user(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=friend_id, invited_id=user_id, status=0).first() else False

    @classmethod
    def is_invited_user(cls, user_id, friend_id):
        return True if cls.objects.filter(user_id=user_id, invited_id=friend_id, status=0).first() else False

    @classmethod
    @hlcache(MC_INVITE_MY_FRIEND_IDS % '{owner_id}')
    def get_invited_my_ids(cls, owner_id):
        return list(cls.objects.filter(invited_id=owner_id,
                                       status=0).order_by('-id').values_list("user_id", flat=True))

    @classmethod
    @hlcache(MC_MY_INVITE_FRIEND_IDS % '{owner_id}')
    def get_my_invited_ids(cls, owner_id):
        return list(cls.objects.filter(user_id=owner_id,
                                       status=0).values_list("invited_id", flat=True))


class Friend(models.Model):
    user_id = models.IntegerField()
    friend_id = models.IntegerField(db_index=True)
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
        return int(friend_id) in friend_ids

    @classmethod
    @hlcache(MC_FRIEND_IDS_KEY % '{user_id}')
    def get_friend_ids(cls, user_id):
        return list(cls.objects.filter(user_id=user_id).values_list("friend_id", flat=True))

    @classmethod
    def get_friends_order_by_date(cls, friend_ids):
        user_dynamics = UserDynamic.objects.filter(user_id__in=friend_ids).order_by("-update_date")

        dynamics_dict = collections.OrderedDict()
        for dynamic in user_dynamics:
            dynamics_dict[dynamic.user_id] = dynamic.to_dict()

        friend_ids = []
        poke_my_user_ids = Poke(user_id=user_id).list()
        if not poke_my_user_ids:
            friend_ids = profiles_dict.keys()
        else:
            friend_ids = poke_my_user_ids
            for uid in profiles_dict.keys():
                if uid not in poke_my_user_ids:
                    friend_ids.append(uid)

        friend_list = []
        for friend_id in friend_ids:
            user_info = dynamics_dict.get(friend_id)
            user_info["user_relation"] = UserEnum.friend.value
            user_info["dynamic"] = friend_dynamic(last_pa_time=user_info["last_pa_time"],
                                                  add_friend_time=self.date,
                                                  paing=user_info["paing"])
            user_info["is_hint"] = True if friend_id in poke_my_user_ids else False
            friend_list.append(user_info)
        return friend_list

        # from live.models import ChannelMember
        # friends = cls.objects.filter(user_id=user_id).order_by("-is_hint", "-update_date")
        # party_user_list = list(ChannelMember.objects.values_list("user_id", flat=True))
        # poke_friend_list = []
        # normal_friend_list = []
        #
        # for friend in friends:
        #     if friend.id in party_user_list:
        #         poke_friend_list.append(friend)
        #     else:
        #         normal_friend_list.append(friend)
        #
        # poke_friend_list.extend(normal_friend_list)
        # return [friend.to_dict() for friend in poke_friend_list]

    @classmethod
    def get_friends_by_online_push(cls, user_id):
        return list(cls.objects.filter(user_id=user_id, push=1).values_list("friend_id", flat=True))

    @classmethod
    def who_is_friends(cls, owner_id, friend_ids):
        quertset = Friend.objects.filter(user_id=owner_id, friend_id__in=friend_ids)
        return list(quertset.values_list("friend_id", flat=True))

    @classmethod
    def add(cls, user_id, friend_id):
        Friend.objects.create(user_id=user_id, friend_id=friend_id)
        Friend.objects.create(user_id=friend_id, friend_id=user_id)

        return True

    @classmethod
    def delete_friend(cls, owner_id, friend_id):
        cls.objects.filter(user_id=owner_id, friend_id=friend_id).delete()
        cls.objects.filter(user_id=friend_id, friend_id=owner_id).delete()
        return True

    @classmethod
    def update_friend_list(cls, friend_id):
        Friend.objects.filter(friend_id=friend_id).update(update_date=timezone.now())

    @classmethod
    def clear_red_point(cls, user_id):
        Friend.objects.filter(user_id=user_id).update(is_hint=False)

    def clear_mc(self):
        redis.delete(MC_FRIEND_IDS_KEY % self.user_id)

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

        if is_invisible:
            redis.hset(REDIS_NO_PUSH_IDS % self.user_id, self.friend_id, is_invisible)
        else:
            redis.hdel(REDIS_NO_PUSH_IDS % self.user_id, self.friend_id)
        return True

    def update_push(self, is_push):
        self.push = is_push
        self.save()

        if is_push:
            redis.hdel(REDIS_NO_PUSH_IDS % self.friend_id, self.user_id)
        else:
            redis.hset(REDIS_NO_PUSH_IDS % self.friend_id, self.user_id, is_push)
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
        friend_ids = cls.get_friend_ids(user_id=user_id)
        friend_list = cls.objects.filter(user_id=user_id, friend_id__in=friend_ids)
        friend_list = [friend.to_dict() for friend in friend_list]

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
        basic_info["dynamic"] = friend_dynamic(owner_id=self.user_id,
                                               user_id=user.id,
                                               add_friend_time=self.date)
        basic_info["pinyin"] = user.pinyin
        return basic_info


# def friend_dynamic(owner_id, user_id, add_friend_time):
def friend_dynamic(last_pa_time, add_friend_time, paing):
    if last_pa_time:
        dt = datetime.datetime.utcfromtimestamp(float(last_pa_time)).replace(tzinfo=pytz.utc)
    else:
        dt = None

    now = timezone.now()
    # 没有开过Pa或者开Pa的时间小于新加的好友的时间
    if not dt:
        if now < add_friend_time + datetime.timedelta(seconds=3600):
            return "你们刚刚成为了好友"

    if dt:
        d = time_format(timezone.localtime(dt))
        if int(friend_profile.get("paing", 0)):
            return "正在开PA"
        elif (now - dt).seconds < 600:
            return "刚刚离开房间"
        elif (now - dt).days < 4:
            return "%s开过PA" % d
        elif (now - dt).days < 30:
            return "%s见过TA" % d

    date_str = time_format(timezone.localtime(add_friend_time))
    return "%s成为朋友" % date_str


def common_friends(user_id, to_user_id):
    user_ids = Friend.get_friend_ids(user_id)
    to_user_id = Friend.get_friend_ids(to_user_id)

    u_ids = set(user_ids) & set(to_user_id)
    return [User.get(uid).nickname for uid in u_ids if User.get(uid)]


@receiver(post_save, sender=Friend)
def save_friend_after(sender, created, instance, **kwargs):
    if created:
        instance.clear_mc()


@receiver(post_delete, sender=Friend)
def delete_friend_after(sender, instance, **kwargs):
    instance.clear_mc()


@receiver(post_save, sender=InviteFriend)
def save_invite_after(sender, created, instance, **kwargs):
    redis.delete(MC_INVITE_MY_FRIEND_IDS % instance.invited_id)
    redis.delete(MC_MY_INVITE_FRIEND_IDS % instance.user_id)


@receiver(post_delete, sender=InviteFriend)
def delete_invite_after(sender, instance, **kwargs):
    redis.delete(MC_INVITE_MY_FRIEND_IDS % instance.invited_id)
    redis.delete(MC_MY_INVITE_FRIEND_IDS % instance.user_id)
