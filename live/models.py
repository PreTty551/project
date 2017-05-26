# -*- coding: utf-8 -*-
import time
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
from .consts import ChannelType, MC_INVITE_PARTY, MC_PA_PUSH_LOCK
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
    def get_friend_channels(cls, user_id, friend_ids=[]):
        if not friend_ids:
            friend_ids = Friend.get_friend_ids(user_id=user_id)

        user_ids = [user_id]
        user_ids.extend(friend_ids)

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
        channels = Channel.objects.filter(channel_id__in=channel_ids)
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
    return "%s%s" % (int(time.time()), user_id)


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
    channel_ids = list(Channel.objects.filter(channel_type=2).values_list("channel_id", flat=True))
    member_ids = list(ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True))
    SocketServer().refresh(user_id=user_id,
                           to_user_id=set(member_ids),
                           message="refresh",
                           event_type=EventType.refresh_public.value)


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

        user = User.get(instance.user_id)
        user.last_pa_time = time.time()

        LiveMediaLog.objects.create(user_id=instance.user_id,
                                    channel_id=instance.channel_id,
                                    channel_type=instance.channel_type,
                                    status=1)

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

    user = User.get(instance.user_id)
    user.last_pa_time = time.time()

    count = ChannelMember.objects.filter(channel_id=instance.channel_id).count()
    if count == 0:
        Channel.objects.filter(channel_id=instance.channel_id).delete()


def party_push(user_id, channel_id, channel_type):
    push_lock = redis.get(MC_PA_PUSH_LOCK % user_id)
    if not push_lock:
        bulk_ids = []
        ids = []
        i = 0

        user = User.get(id=user_id)
        # friend_ids = Friend.get_friends_by_online_push(user_id=user_id)
        # party_friend_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("user_id", flat=True)
        # no_party_friend_ids = set(party_friend_ids) ^ set(friend_ids)
        #
        # pre_week = timezone.now() - datetime.timedelta(days=7)
        # party_user_ids_in_week = list(LiveMediaLog.objects.filter(date__gte=pre_week, user_id__in=no_party_friend_ids)
        #                                                   .values_list("user_id", flat=True).distinct())

        # for friend_id in party_user_ids_in_week:
        #     fids = Friend.get_friend_ids(user_id=friend_id)
        #     if int(user_id) in fids:
        #         fids.remove(int(user_id))
        #     if int(friend_id) in fids:
        #         fids.remove(int(friend_id))
        #
        #     party_user_ids = ChannelMember.objects.filter(user_id__in=fids).values_list("user_id", flat=True)
        #     nicknames = [User.get(id=uid).nickname for uid in party_user_ids]
        #     if nicknames:
        #         nicknames = ",".join(nicknames)
        #         message = "%s 正在开PA" % nicknames
        #         JPush().async_push(user_ids=[friend_id],
        #                            message=message,
        #                            push_type=1,
        #                            channel_id=channel_id,
        #                            channel_type=channel_type)
        #         SocketServer().invite_party_in_live(user_id=user.id,
        #                                             to_user_id=friend_id,
        #                                             message=message,
        #                                             channel_id=channel_id)

        party_friend_ids = Friend.get_friend_ids(user_id=user_id)
        message = "%s 正在开PA" % user.nickname
        JPush(user_id=user_id).async_batch_push(user_ids=party_friend_ids,
                                                message=message,
                                                push_type=1,
                                                channel_id=channel_id,
                                                channel_type=channel_type)

        redis.set(MC_PA_PUSH_LOCK % user_id, 1, 300)
