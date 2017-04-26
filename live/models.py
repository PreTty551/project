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

    @classmethod
    @transaction.atomic()
    def _add(cls, channel_id, user_id, channel_type):
        obj = cls.objects.create(creator_id=user_id, channel_id=channel_id, channel_type=channel_type)
        if obj:
            ChannelMember.add(channel_id=channel_id, user_id=user_id)
            ChannelMember.objects.exclude(channel_id=obj.channel_id).filter(user_id=user_id).delete()
            return obj
        return None

    @classmethod
    def create_channel(cls, user_id, channel_type):
        channel_id = unique_channel_id(user_id=user_id)
        return cls._add(channel_id=channel_id,
                        user_id=user_id,
                        channel_type=channel_type)

    @classmethod
    def get_channel(cls, channel_id):
        return cls.objects.filter(channel_id=channel_id).first()

    @classmethod
    def invite_channel(cls, user_id, invite_user_id):
        pass

    @classmethod
    @transaction.atomic()
    def delete_channel(cls, channel_id):
        channel = cls.objects.filter(channel_id=channel_id).first()
        if channel:
            ChannelMember.objects.filter(channel_id=channel_id).delete()

            # from answer.utils import send_msg
            # token = "78c21f9d53c94182867abe411804ba46ec353b7a7426df2f870a1437e9c79fe3"
            # msg = u"房间%s被清除" % channel_id
            # send_msg(msg, token)

    @classmethod
    def join_channel(cls, channel_id, user_id):
        channel = cls.objects.filter(channel_id=channel_id).first()
        if channel:
            ChannelMember.add(channel_id=channel_id, user_id=user_id)
            ChannelMember.objects.exclude(channel_id=channel.channel_id).filter(user_id=user_id).delete()
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

    @property
    def title(self):
        if self.name:
            return self.name

        nicknames = []
        user_ids = self.get_channel_member()
        for user_id in user_ids:
            user = User.get(user_id)
            if not user:
                continue
            nicknames.append(user.nickname)
        title = ",".join(nicknames)
        return "%s%s" % ("", title)

    @property
    def duration_time(self):
        timedelta = timezone.now() - self.date
        minute = int((timedelta.seconds / 60) + timedelta.days * 24 * 60)
        return "当前%s人, 进行了%s分钟" % (self.member_count, minute)

    @property
    def icon(self):
        member = ChannelMember.objects.filter(channel_id=self.channel_id).first()
        if member:
            user = User.get(member.user_id)
            if user:
                return user.avatar_url
        return ""

    def to_dict(self):
        return {
            "title": self.title,
            "channel_id": self.channel_id,
            "duration_time": self.duration_time,
            "icon": self.icon,
            "is_lock": self.is_lock,
            "date": self.date,
            "member_count": self.member_count,
            "channel_type": self.channel_type
        }


class InviteChannel(models.Model):
    user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    channel_id = models.CharField(max_length=50)
    status = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def add(cls, user_id, to_user_id, channel_id):
        return cls.objects.create(user_id=user_id,
                                  to_user_id=to_user_id,
                                  channel_id=channel_id)


class ChannelMember(models.Model):
    channel_id = models.CharField(max_length=50)
    user_id = models.IntegerField()
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
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
        for o in cls.objects.filter(user_id=user_id):
            o.delete()


class LiveMediaLog(models.Model):
    user_id = models.IntegerField()
    channel_id = models.CharField(max_length=50)
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
        LiveMediaLog.objects.create(user_id=instance.user_id,
                                    channel_id=instance.channel_id,
                                    status=1)

        channel = Channel.get_channel(channel_id=instance.channel_id)
        channel.member_count = F("member_count") + 1
        channel.save()

        InviteParty.objects.filter(to_user_id=instance.user_id, status=0).update(status=1)
        redis.delete(MC_INVITE_PARTY % instance.user_id)

        refresh(instance.user_id)


@receiver(post_delete, sender=ChannelMember)
def delete_member_after(sender, instance, **kwargs):
    LiveMediaLog.objects.filter(user_id=instance.user_id, channel_id=instance.channel_id, status=1) \
                        .update(end_date=timezone.now(), status=2)

    channel = Channel.get_channel(channel_id=instance.channel_id)
    if channel:
        channel.member_count = F("member_count") - 1
        channel.save()

        member_count = ChannelMember.objects.filter(channel_id=instance.channel_id).count()
        if member_count == 0:
            Channel.objects.filter(channel_id=instance.channel_id).delete()

        refresh(instance.user_id)


@receiver(post_save, sender=Channel)
def add_channel_after(sender, created, instance, **kwargs):
    if created:
        push_lock = redis.get("mc:user:%s:pa_push_lock" % request.user.id)
        if not push_lock:
            bulk_ids = []
            ids = []
            i = 0

            user = User.get(id=instance.creator_id)
            friend_ids = Friend.get_friend_ids(user_id=instance.creator_id)
            pre_week = timezone.now() - datetime.timedelta(days=7)
            party_user_ids_in_week = list(LiveMediaLog.objects.filter(date__gte=pre_week, user_id__in=friend_ids)
                                                              .values_list("user_id", flat=True).distinct())
            bulk_user_ids = set(party_user_ids_in_week) ^ set(friend_ids)

            message = "%s 正在开PA" % user.nickname
            JPush().async_push(user_ids=bulk_user_ids, message=message)
            SocketServer().invite_party_in_live(user_id=user.id,
                                                to_user_id=bulk_user_ids,
                                                message=message,
                                                channel_id=instance.channel_id)

            for friend_id in party_user_ids_in_week:
                if i < 11:
                    fids = Friend.get_friend_ids(user_id=friend_id)
                    party_user_ids = ChannelMember.objects.filter(user_id__in=fids).values_list("user_id", flat=True)
                    nicknames = [User.get(id=uid).nickname for uid in party_user_ids]
                    nicknames = ",".join(nicknames)
                    message = "%s 正在开PA" % nicknames
                    JPush().async_push(user_ids=[friend_id], message=message)
                    SocketServer().invite_party_in_live(user_id=user.id,
                                                        to_user_id=friend_id,
                                                        message=message,
                                                        channel_id=instance.channel_id)
                    i += 1

            redis.get("mc:user:%s:pa_push_lock" % request.user.id, 1, 60)
