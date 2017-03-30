# -*- coding: utf-8 -*-
import time
import datetime
import subprocess

from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models import F, Sum
from django.utils import timezone

from user.models import User


REDIS_CHANNEL_MEMBER_KEY = "agora:channel:%s:uids"
REDIS_CHANNEL_GIFT_QUEEN = "channel:%s:gifts"


class Channel(models.Model):
    name = models.CharField(max_length=100, default="")
    channel_id = models.CharField(unique=True, max_length=50)
    member_count = models.SmallIntegerField(default=0)
    channel_type = models.SmallIntegerField(default=0)
    date = models.DateTimeField('date', auto_now_add=True)
    pid = models.IntegerField(default=0)

    @classmethod
    @transaction.atomic()
    def _add(cls, channel_id, user_id):
        obj = cls.objects.create(channel_id=channel_id)
        if obj:
            ChannelMember.add(channel_id=channel_id, user_id=user_id)
            ChannelMember.objects.exclude(channel_id=obj.channel_id).filter(user_id=user_id).delete()
            return obj
        return None

    @classmethod
    def create_channel(cls, user_id):
        channel_id = unique_channel_id(user_id=user_id)
        return cls._add(channel_id=channel_id, user_id=user_id)

    @classmethod
    def get_channel(cls, channel_id):
        return cls.objects.filter(channel_id=channel_id).first()

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
    def join_channel(cls, channel_id, user_id, in_channel_uids=[]):
        channel = cls.objects.filter(channel_id=channel_id).first()
        if channel:
            ChannelMember.add(channel_id=channel_id, user_id=user_id)
            ChannelMember.objects.exclude(channel_id=channel.channel_id).filter(user_id=user_id).delete()
            return True
        return False

    @property
    def is_lock(self):
        return self.channel_type == 1

    def lock(self):
        self.channel_type = 1
        self.save()

    def unlock(self):
        self.channel_type = 0
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

        user_ids = self.get_channel_member()
        nicknames = [User.get(user_id).nickname for user_id in user_ids]
        title = ",".join(nicknames)
        return "%s%s" % ("", title)

    @property
    def duration_time(self):
        timedelta = timezone.now() - self.date
        minute = (timedelta.seconds / 60) + timedelta.days * 24 * 60
        return "当前%s人, 进行了%s分钟" % (self.member_count, minute)

    @property
    def icon(self):
        member = ChannelMember.objects.filter(channel_id=self.channel_id).first()
        if member:
            return User.get(member.user_id).avatar_url
        return ""

    def to_dict(self):
        return {
            "title": self.title,
            "channel_id": self.channel_id,
            "duration_time": self.duration_time,
            "icon": self.icon,
            "is_lock": self.is_lock,
            "date": self.date,
            "member_count": self.member_count
        }


class ChannelMember(models.Model):
    channel_id = models.CharField(max_length=50)
    user_id = models.IntegerField()
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        unique_together = (('channel_id', 'user_id'))

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


def unique_channel_id(user_id):
    return "%s%s" % (int(time.time()), user_id)


@receiver(post_save, sender=ChannelMember)
def add_member_after(sender, created, instance, **kwargs):
    if created:
        LiveMediaLog.objects.create(user_id=instance.user_id,
                                    channel_id=instance.channel_id,
                                    status=1)

        channel = Channel.get_channel(channel_id=instance.channel_id)
        channel.member_count = F("member_count") + 1
        channel.save()


@receiver(post_delete, sender=ChannelMember)
def delete_member_after(sender, instance, **kwargs):
    LiveMediaLog.objects.filter(user_id=instance.user_id, channel_id=instance.channel_id, status=1) \
                        .update(end_date=timezone.now(), status=2)
    channel = Channel.get_channel(channel_id=instance.channel_id)
    if channel:
        channel.member_count = F("member_count") - 1
        channel.save()

        channel = Channel.get_channel(channel_id=instance.channel_id)
        if Channel.objects.filter(channel_id=instance.channel_id).count() == 0:
            channel.delete()
            subprocess.Popen(["kill", str(channel.pid)])


@receiver(post_save, sender=Channel)
def create_process(sender, created, instance, **kwargs):
    if created:
        p = subprocess.Popen(["python", "manage.py", "gift_queue", str(instance.channel_id)])
        if p:
            instance.pid = p.pid
            instance.save()
