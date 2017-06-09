# -*- coding: utf-8 -*-
import time
import random
import datetime
import subprocess
import django_rq

from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models import F, Sum
from django.utils import timezone

from corelib.rongcloud import RongCloud
from corelib.mc import hlcache
from corelib.redis import redis
from corelib.jiguang import JPush

from user.models import User, Friend
from user.consts import REDIS_NO_PUSH_IDS
from .consts import ChannelType, MC_INVITE_PARTY, MC_PA_PUSH_LOCK, REDIS_PUBLIC_PA_IDS, \
                    REDIS_PUBLIC_LOCK
from socket_server import SocketServer, EventType


class Channel(models.Model):
    name = models.CharField(max_length=100, default="")
    channel_id = models.CharField(unique=True, max_length=50)
    creator_id = models.IntegerField(default=0)
    member_count = models.SmallIntegerField(default=0)
    channel_type = models.SmallIntegerField(default=0)
    is_lock = models.BooleanField(default=False)
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        db_table = 'channel'

    @classmethod
    def _add(cls, channel_id, user_id, channel_type, nickname):
        obj = cls.objects.create(creator_id=user_id, channel_id=channel_id, channel_type=channel_type)
        if obj:
            user = User.get(user_id)
            ChannelMember.add(channel_id=channel_id, channel_type=obj.channel_type, user_id=user_id, nickname=nickname)
            ChannelMember.objects.filter(user_id=user_id).exclude(channel_id=channel_id).delete()
            return obj
        return None

    @classmethod
    def create_channel(cls, user_id, channel_type, nickname):
        channel_id = unique_channel_id(user_id=user_id)
        return cls._add(channel_id=channel_id,
                        user_id=user_id,
                        channel_type=channel_type,
                        nickname=nickname)

    @classmethod
    def get_channel(cls, channel_id):
        return cls.objects.filter(channel_id=channel_id).first()

    @classmethod
    def invite_channel(cls, user_id, invite_user_id):
        pass

    @classmethod
    def join_channel(cls, channel_id, channel_type, user_id, nickname):
        channel = Channel.get_channel(channel_id=channel_id)
        if channel:
            ChannelMember.add(channel_id=channel_id, channel_type=channel_type, user_id=user_id, nickname=nickname)
            ChannelMember.objects.filter(user_id=user_id).exclude(channel_id=channel.channel_id).delete()
            return True
        return False

    def delete_channel(self):
        for member in ChannelMember.objects.filter(channel_id=self.channel_id):
            member.delete()
            user = User.get(member.user_id)
            user.paing = 0
        return True

    def quit_channel(self, user_id):
        ChannelMember.objects.filter(user_id=user_id, channel_id=self.channel_id).delete()
        return True

    def lock(self):
        self.is_lock = True
        self.save()

    def unlock(self):
        self.is_lock = False
        self.save()

    @classmethod
    def channel_member_count(cls):
        return ChannelMember.objects.all().count()
        return cls.objects.all().aggregate(Sum("member_count"))["member_count__sum"] or 0

    @classmethod
    def get_channel_by_channeltype(cls, channel_ids, channel_type):
        if channel_type:
            return Channel.objects.filter(channel_id__in=channel_ids,
                                          channel_type=channel_type)
        return Channel.objects.filter(channel_id__in=channel_ids)

    @classmethod
    def get_friend_channels(cls, user_id, friend_ids=[], channel_type=0):
        if not friend_ids:
            friend_ids = Friend.get_friend_ids(user_id=user_id)

        user_ids = [user_id]
        user_ids.extend(friend_ids)

        # 兼职人员互相看不到
        from ida.models import Duty
        ignore_user_ids = list(Duty.objects.values_list("user_id", flat=True))
        if user_id in ignore_user_ids:
            ignore_user_ids.remove(int(user_id))
            channel_ids = list(ChannelMember.objects.filter(user_id__in=user_ids)
                                                    .exclude(user_id__in=ignore_user_ids)
                                                    .values_list("channel_id", flat=True))
        else:
            channel_ids = list(ChannelMember.objects.filter(user_id__in=user_ids).values_list("channel_id", flat=True))
        member_list = ChannelMember.objects.filter(channel_id__in=channel_ids)

        members = []
        members_dict = {}
        channel_user_ids = []
        for member in member_list:
            _ = members_dict.setdefault(member.channel_id, [])
            _.append((member.user_id, member.nickname))
            channel_user_ids.append(member.user_id)

        results = []
        channels = cls.get_channel_by_channeltype(channel_ids=channel_ids, channel_type=channel_type)
        for channel in channels:
            member = members_dict.get(channel.channel_id)
            if not member:
                continue

            friend_nicknames = []
            user_icon = None
            for user_id, nickname in member:
                if user_id in friend_ids:
                    user_icon = user_id
                    friend_nicknames.append((nickname, 0))
                else:
                    friend_nicknames.append((nickname, 1))

                if not user_icon:
                    user_icon = user_id

            friend_nicknames = sorted(friend_nicknames, key=lambda item: item[1])
            user = User.get(user_icon)
            icon = user.avatar_url
            results.append(channel.to_dict(nicknames=friend_nicknames, icon=icon))

        return results

    def title(self, nicknames=[]):
        nicknames = [nickname_tuple[0] for nickname_tuple in nicknames]
        return ",".join(nicknames)

    def duration_time(self, nicknames):
        timedelta = timezone.now() - self.date
        minute = int((timedelta.seconds / 60) + timedelta.days * 24 * 60)
        people_number = self._member_count(nicknames=nicknames)
        if minute < 1:
            return "当前%s人, 刚刚开PA" % people_number
        return "当前%s人, 进行了%s分钟" % (people_number, minute)

    def _member_count(self, nicknames):
        return len(nicknames)

    def icon(self, user_id):
        user = User.get(user_id)
        if user:
            return user.avatar_url
        return ""

    def to_dict(self, nicknames, icon=""):
        title = self.title(nicknames)
        return {
            "title": title,
            "channel_id": self.channel_id,
            "duration_time": self.duration_time(nicknames=nicknames),
            "icon": icon,
            "is_lock": self.is_lock,
            "date": self.date,
            "member_count": len(nicknames),
            "channel_type": self.channel_type
        }


class ChannelMember(models.Model):
    channel_id = models.CharField(max_length=50)
    channel_type = models.SmallIntegerField(default=0)
    user_id = models.IntegerField(db_index=True)
    nickname = models.CharField(max_length=50, default="")
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        db_table = "channel_member"
        unique_together = (('channel_id', 'user_id'))

    @classmethod
    def get_channel(cls, user_id):
        return cls.objects.filter(user_id=user_id).first()

    @classmethod
    def add(cls, channel_id, channel_type, user_id, nickname):
        member = cls.objects.filter(channel_id=channel_id, user_id=user_id).first()
        if not member:
            cls.objects.create(channel_id=channel_id, channel_type=channel_type, user_id=user_id, nickname=nickname)

    @classmethod
    def clear_channel(cls, user_id):
        cls.objects.filter(user_id=user_id).delete()


class LiveLockLog(models.Model):
    channel_id = models.CharField(max_length=50)
    member_count = models.SmallIntegerField()
    status = models.SmallIntegerField(default=0)
    date = models.DateTimeField('date', auto_now_add=True)
    end_date = models.DateTimeField('end_date', default=datetime.datetime.now)

    class Meta:
        db_table = "live_lock_log"


class LiveMediaLog(models.Model):
    user_id = models.IntegerField(db_index=True)
    channel_id = models.CharField(max_length=50)
    channel_type = models.SmallIntegerField(default=0)
    type = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField()
    date = models.DateTimeField('date', auto_now_add=True)
    end_date = models.DateTimeField('end_date', default=datetime.datetime.now)

    class Meta:
        db_table = "live_media_log"


class GuessWord(models.Model):
    content = models.CharField(max_length=100)
    date = models.DateTimeField('date', auto_now_add=True)

    @classmethod
    def get_random_word(cls):
        obj = cls.objects.all().order_by("?").first()
        if obj:
            return obj.content
        return ""


class InviteParty(models.Model):
    user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    channel_id = models.CharField(max_length=50, default="")
    party_type = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=0)
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        db_table = "invite_party"

    @classmethod
    def add(cls, user_id, to_user_id, party_type, channel_id=""):
        return cls.objects.create(user_id=user_id,
                                  to_user_id=to_user_id,
                                  party_type=party_type,
                                  channel_id=channel_id)

    @classmethod
    def clear(cls, user_id):
        redis.delete(MC_INVITE_PARTY % user_id)
        cls.objects.filter(user_id=user_id).update(status=1)

    @classmethod
    # @hlcache(MC_INVITE_PARTY % '{user_id}')
    def get_invites(cls, user_id):
        queryset = cls.objects.filter(to_user_id=user_id, status=0).values_list("user_id", flat=True).distinct()
        return list(queryset)


def unique_channel_id(user_id):
    return "%s%s%s" % (int(time.time() * 1000), random.randint(0, 400), user_id)


def _refresh_friend(user_id):
    friend_ids = Friend.get_friend_ids(user_id)
    online_ids = User.get_online_ids()
    online_friend_ids = [friend_id for friend_id in friend_ids if friend_id in online_ids]
    online_friend_ids.append(user_id)
    if online_friend_ids:
        SocketServer().refresh(user_id=user_id,
                               to_user_id=set(online_friend_ids),
                               message="refresh",
                               event_type=EventType.refresh_home.value)
        SocketServer().refresh(user_id=user_id,
                               to_user_id=set(online_friend_ids),
                               message="refresh",
                               event_type=EventType.refresh_inner_home.value)


def _refresh_public(user_id):
    # channel_ids = list(Channel.objects.filter(channel_type=2).values_list("channel_id", flat=True))
    # member_ids = list(ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True))
    lock = redis.get(REDIS_PUBLIC_LOCK)
    if not lock:
        uids = redis.hkeys(REDIS_PUBLIC_PA_IDS)
        member_ids = [uid.decode() for uid in uids]
        SocketServer().refresh(user_id=user_id,
                               to_user_id=set(member_ids),
                               message="refresh",
                               event_type=EventType.refresh_public.value)
        redis.set(REDIS_PUBLIC_LOCK, 1, 5)


def refresh(user_id, channel_type):
    queue = django_rq.get_queue('refresh')
    if channel_type == 2:
        queue.enqueue(_refresh_public, user_id)
    else:
        queue.enqueue(_refresh_friend, user_id)


@receiver(post_save, sender=ChannelMember)
def add_member_after(sender, created, instance, **kwargs):
    if created:
        push_lock = redis.get(MC_PA_PUSH_LOCK % instance.user_id)
        if push_lock:
            redis.set(MC_PA_PUSH_LOCK % instance.user_id, 1, 300)

        LiveMediaLog.objects.create(user_id=instance.user_id,
                                    channel_id=instance.channel_id,
                                    channel_type=instance.channel_type,
                                    status=1)

        if instance.channel_type == 2:
            redis.hset(REDIS_PUBLIC_PA_IDS, instance.user_id, 1)

        # ========= 以下是异步操作 =========

        # 刷新好友列表顺序和清除红点
        queue = django_rq.get_queue('high')
        queue.enqueue(Friend.update_friend_list, instance.user_id)
        queue.enqueue(Friend.clear_red_point, instance.user_id)

        # 客户端刷新
        refresh(instance.user_id, instance.channel_type)


@receiver(post_delete, sender=ChannelMember)
def delete_member_after(sender, instance, **kwargs):
    LiveMediaLog.objects.filter(user_id=instance.user_id,
                                channel_id=instance.channel_id,
                                status=1) \
                        .update(end_date=timezone.now(), status=2)

    redis.hdel(REDIS_PUBLIC_PA_IDS, instance.user_id)

    count = ChannelMember.objects.filter(channel_id=instance.channel_id).count()
    if count == 0:
        Channel.objects.filter(channel_id=instance.channel_id).delete()


def party_push(user_id, channel_id, channel_type):
    push_lock = redis.get(MC_PA_PUSH_LOCK % user_id)
    if not push_lock:
        friend_ids = Friend.get_friend_ids(user_id)
        party_friend_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("user_id", flat=True)
        no_party_friend_ids = set(party_friend_ids) ^ set(friend_ids)

        pre_week = timezone.now() - datetime.timedelta(days=7)
        party_user_ids_in_week = list(LiveMediaLog.objects.filter(date__gte=pre_week, user_id__in=no_party_friend_ids)
                                                          .values_list("user_id", flat=True).distinct())

        for friend_id in party_user_ids_in_week:
            fids = Friend.get_friend_ids(user_id=friend_id)
            if int(friend_id) in fids:
                fids.remove(int(friend_id))

            party_user_ids = ChannelMember.objects.filter(user_id__in=fids).values_list("user_id", flat=True)
            nicknames = [User.get(id=uid).nickname for uid in party_user_ids]
            if nicknames:
                nicknames = ",".join(nicknames)
                message = "%s 正在开PA" % nicknames
                JPush().async_push(user_ids=[friend_id],
                                   message=message,
                                   push_type=1,
                                   channel_id=channel_id,
                                   channel_type=channel_type,
                                   apns_collapse_id="pa")

        redis.set(MC_PA_PUSH_LOCK % user_id, 1, 60)
