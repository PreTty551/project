# -*- coding: utf-8 -*-
import time
import datetime
import subprocess

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
from .consts import ChannelType, MC_INVITE_PARTY
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
            ChannelMember.add(channel_id=channel_id, user_id=user_id, nickname=nickname)
            ChannelMember.objects.filter(user_id=user_id).exclude(channel_id=channel_id).delete()
            # redis.lpush(REDIS_CHANNEL_MEMBERS % channel.id, user.nickname)
            # redis.lpush(REDIS_CHANNEL_NICKNAMES % channel.id, user.nickname)
            # redis.incr(REDIS_CHANNEL_MEMBER_COUNT % channel.id)
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
    def delete_channel(cls, channel_id):
        channel = cls.objects.filter(channel_id=channel_id).first()
        if channel:
            ChannelMember.objects.filter(channel_id=channel_id).delete()

    @classmethod
    def join_channel(cls, channel_id, user_id):
        channel = Channel.get_channel(channel_id=channel_id)
        if channel:
            ChannelMember.add(channel_id=channel_id, user_id=user_id)
            ChannelMember.objects.filter(user_id=user_id).exclude(channel_id=channel.channel_id).delete()
            return True
        return False

    def lock(self):
        self.is_lock = True
        self.save()

    def unlock(self):
        self.is_lock = False
        self.save()

    def quit_channel(self, user_id):
        ChannelMember.objects.filter(user_id=user_id, channel_id=self.channel_id).delete()

    def get_channel_member(self):
        return ChannelMember.get_channel_member(channel_id=self.channel_id)

    def add_channel_member(self, user_id):
        ChannelMember.add(channel_id=self.channel_id, user_id=user_id)

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

        channel_ids = ChannelMember.objects.filter(user_id__in=user_ids).values_list("channel_id", flat=True)
        member_list = ChannelMember.objects.filter(channel_id__in=channel_ids)

        members = []
        members_dict = {}
        channel_user_ids = []
        for member in member_list:
            _ = members_dict.setdefault(member.channel_id, [])
            _.append((member.user_id, member.nickname))
            channel_user_ids.append(member.user_id)

        results = []
        channels = Channel.objects.filter(channel_id__in=channel_ids, channel_type=ChannelType.normal.value)
        for channel in channels:
            member = members_dict.get(channel.channel_id)
            if not member:
                continue

            friend_nicknames = []
            user_icon = None
            for user_id, nickname in member:
                if user_id in channel_friend_ids:
                    user_icon = user_id
                    friend_nicknames.append((nickname, 1))
                else:
                    friend_nicknames.append((nickname, 0))

                if not user_icon:
                    user_icon = user_id

            friend_nicknames = sorted(friend_nicknames, key=lambda item: item[1])
            user = User.get(user_icon)
            icon = user.avatar_url
            results.append(channel.to_dict(nicknames=friend_nicknames, icon=icon))

        return results

    @property
    def title(self, nicknames=[]):
        # nicknames = redis.lrange(REDIS_CHANNEL_NICKNAMES % self.id, 0, -1)
        # nicknames = [nickname.decode() for nickname in nicknames]
        return ",".join(nicknames)

    @property
    def duration_time(self):
        timedelta = timezone.now() - self.date
        minute = int((timedelta.seconds / 60) + timedelta.days * 24 * 60)
        number = len(self.name.split(","))
        if minute < 1:
            return "当前%s人, 刚刚开PA" % number
        return "当前%s人, 进行了%s分钟" % (number, minute)

    def icon(self, user_id):
        user = User.get(user_id)
        if user:
            return user.avatar_url
        return ""

    def to_dict(self, nicknames):
        title = self.title(nicknames)
        return {
            "title": title,
            "channel_id": self.channel_id,
            "duration_time": self.duration_time,
            "icon": self.icon(user_id=friend_id),
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
    def get_channel_member(cls, channel_id):
        return cls.objects.filter(channel_id=channel_id).values_list("user_id", flat=True)

    @classmethod
    def add(cls, channel_id, user_id):
        member = cls.objects.filter(channel_id=channel_id, user_id=user_id).first()
        if not member:
            cls.objects.create(channel_id=channel_id, user_id=user_id)

    @classmethod
    def clear_channel(cls, user_id):
        cls.objects.filter(user_id=user_id).delete()


class LiveLockLog(models.Model):
    channel_id = models.CharField(max_length=50)
    member_count = models.SmallIntegerField()
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


def refresh(user_id):
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


def refresh_public(user_id):
    channel_ids = list(Channel.objects.filter(channel_type=2).values_list("channel_id", flat=True))
    member_ids = list(ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True))
    SocketServer().refresh(user_id=user_id,
                           to_user_id=set(member_ids),
                           message="refresh",
                           event_type=EventType.refresh_public.value)


@receiver(post_delete, sender=Channel)
def delete_channel_after(sender, instance, **kwargs):
    redis.delete(REDIS_CHANNEL_MEMBER_COUNT % instance.id)


@receiver(post_save, sender=InviteParty)
def add_invite_party(sender, created, instance, **kwargs):
    if created:
        InviteParty.objects.filter(user_id=instance.to_user_id,
                                   to_user_id=instance.user_id,
                                   status=0).update(status=1)
        redis.delete(MC_INVITE_PARTY % instance.user_id)


@receiver(post_save, sender=ChannelMember)
def add_member_after(sender, created, instance, **kwargs):
    if created:
        push_lock = redis.get("mc:user:%s:pa_push_lock" % instance.user_id)
        if push_lock:
            redis.set("mc:user:%s:pa_push_lock" % instance.user_id, 1, 300)

        channel = Channel.objects.filter(channel_id=instance.channel_id).first()
        LiveMediaLog.objects.create(user_id=instance.user_id,
                                    channel_id=instance.channel_id,
                                    channel_type=channel.channel_type,
                                    status=1)

        Friend.objects.filter(friend_id=instance.user_id).update(update_date=timezone.now())
        Friend.objects.filter(user_id=instance.user_id).update(is_hint=False)

        user = User.get(instance.user_id)
        user.last_pa_time = time.time()
        user.paing = 1

        if channel.channel_type == 2:
            refresh_public(instance.user_id)
        else:
            refresh(instance.user_id)

        count = ChannelMember.objects.filter(user_id=instance.user_id).count()
        if count > 1:
            party_push(instance.user_id, instance.channel_id, channel.channel_type)


@receiver(post_delete, sender=ChannelMember)
def delete_member_after(sender, instance, **kwargs):
    LiveMediaLog.objects.filter(user_id=instance.user_id, channel_id=instance.channel_id, status=1) \
                        .update(end_date=timezone.now(), status=2)

    channel = Channel.get_channel(channel_id=instance.channel_id)
    if channel:
        count = ChannelMember.objects.filter(channel_id=instance.channel_id).count()
        if count == 0:
            Channel.objects.filter(channel_id=instance.channel_id).delete()
        else:
            user = User.get(instance.user_id)
            name = channel.name.replace("%s," % user.nickname, "").replace(",%s" % user.nickname, "")
            name = name.strip(",")
            if name:
                channel.name = name
                channel.save()

        user = User.get(instance.user_id)
        user.last_pa_time = time.time()
        user.paing = 0

        if channel.channel_type == 2:
            refresh_public(instance.user_id)
        else:
            refresh(instance.user_id)


def party_push(user_id, channel_id, channel_type):
    push_lock = redis.get("mc:user:%s:pa_push_lock" % user_id)
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
        JPush().async_batch_push(user_ids=party_friend_ids,
                                 message=message,
                                 push_type=1, channel_id=channel_id, channel_type=channel_type)

        redis.set("mc:user:%s:pa_push_lock" % user_id, 1, 300)
