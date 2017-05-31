# -*- coding: utf-8 -*-
import uuid
import random
import datetime

from datetime import date, timedelta
from itertools import permutations
from xpinyin import Pinyin

from django.utils import timezone
from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from django.contrib.auth import models as auth_models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager

from corelib.qiniucloud import Qiniu
from corelib.props import PropsMixin
from corelib.weibo import Weibo
from corelib.utils import natural_time as time_format
from corelib.mc import cache
from corelib.redis import redis

from user.consts import UserEnum, MC_USER_KEY, EMOJI_LIST, REDIS_ONLINE_USERS_KEY, \
                        REDIS_NO_PUSH_IDS, REDIS_ONLINE_USERS
from .place import Place


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, mobile="", **extra_fields):
        extra_fields.setdefault('nickname', '')
        if not mobile:
            mobile = random.randint(11100000000, 11200000000)
        user = self.model(
            nickname=extra_fields['nickname'],
            username=username,
            email=BaseUserManager.normalize_email(email),
            mobile=mobile
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def add_user(self, nickname, gender=0, mobile="", version="", platform=0):
        try:
            name = str(uuid.uuid4())[:30]
            pinyin = Pinyin().get_pinyin(nickname, "")
            password = name
            email = "%s@%s.com" % (name, name)
            user = self._create_user(username=name, email=email, password=password, nickname=nickname, mobile=mobile)
            user.mobile = mobile
            user.gender = gender
            user.platform = platform
            user.pinyin = pinyin
            user.paid = user.id
            user.save()
            return user
        except Exception as e:
            return None

    def filter_nickname(self, nickname):
        return super(UserManager, self).get_queryset().filter(nickname=nickname).first()


@transaction.atomic()
def create_third_user(third_id, third_name, nickname, avatar, gender, mobile, platform, version):
    nickname = nickname.replace(" ", "").replace("#", "").replace("@", "")
    user = User.objects.filter(mobile=mobile).first()
    if not user:
        user = User.objects.add_user(nickname=nickname,
                                     gender=gender,
                                     mobile=mobile,
                                     platform=platform,
                                     version=version)
    ThirdUser.objects.create(mobile=mobile, third_id=third_id, third_name=third_name)
    return user


def update_avatar_in_third_login(avatar_url, user_id):
    user = User.get(user_id)
    if not avatar_url:
        return

    from corelib.kingsoft.ks3 import KS3
    avatar_name = KS3().fetch_avatar(url=avatar_url, user_id=user_id)
    if avatar_name:
        user.avatar = avatar_name
        user.save()


class User(AbstractUser, PropsMixin):
    paid = models.CharField(max_length=50, unique=True, null=True, blank=True)
    nickname = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20, unique=True)
    avatar = models.CharField(max_length=40, default="")
    gender = models.SmallIntegerField(default=0)
    intro = models.CharField(max_length=100, default="")
    country = models.CharField(max_length=20, default="")
    country_code = models.CharField(max_length=10, default="")
    is_contact = models.BooleanField(default=False)
    platform = models.SmallIntegerField(default=0)
    version = models.CharField(max_length=10, default="")
    pinyin = models.CharField(max_length=50, default="")
    online_time = models.DateTimeField(default=timezone.now)
    offline_time = models.DateTimeField(default=timezone.now)
    rong_token = models.CharField(max_length=100, default="")

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = u'用户'
        verbose_name_plural = u'用户列表'

    # def __getattr__(self, attr):
    #     try:
    #         return object.__getattr__(self, attr)
    #     except AttributeError:
    #         return ""
    #
    # def __str__(self):
    #     return "<User(id=%s, nickname=%s)>" % (self.id, self.nickname)
    #
    # __repr__ = __str__

    @classmethod
    def add(cls, user_id):
        cls.objects.create(user_id=user_id)

    @property
    def _props_db_key(self):
        return "db:user:%s" % self.id

    def save(self, *args, **kwargs):
        if not self.mobile:
            self.mobile = random.randint(27600000000, 27690000000)
        super(User, self).save(*args, **kwargs)

    @classmethod
    @cache(MC_USER_KEY % '{id}')
    def get(cls, id):
        return cls.objects.filter(id=id).first()

    def online(self):
        self.online_time = timezone.now()
        self.save()
        redis.hset(REDIS_ONLINE_USERS_KEY, self.id, 1)
        redis.hset(REDIS_ONLINE_USERS, self.id, 1)

    def offline(self):
        self.offline_time = timezone.now()
        self.save()
        self.paing = 0
        redis.hdel(REDIS_ONLINE_USERS_KEY, self.id)
        redis.hdel(REDIS_ONLINE_USERS, self.id)
        from live.models import ChannelMember
        ChannelMember.objects.filter(user_id=self.id).delete()

    def is_online(self):
        return redis.hget(REDIS_ONLINE_USERS_KEY, self.id)

    @classmethod
    def get_profile(cls, user_id):
        _ = redis.hgetall("db:user:%s" % user_id)
        profile = {}
        for k, v in _.items():
            profile[k.decode()] = v.decode()
        return profile

    @classmethod
    def get_online_ids(cls):
        return [int(user_id) for user_id in redis.hkeys(REDIS_ONLINE_USERS)]

    def binding_wechat(self, third_id):
        ThirdUser.objects.create(mobile=self.mobile, third_id=third_id, third_name="wx")
        return True

    def binding_weibo(self, third_id):
        ThirdUser.objects.create(mobile=self.mobile, third_id=third_id, third_name="wb")
        return True

    def unbinding_wechat(self):
        ThirdUser.objects.filter(mobile=self.mobile, third_name="wx").delete()
        return True

    def unbinding_weibo(self):
        ThirdUser.objects.filter(mobile=self.mobile, third_name="wb").delete()
        return True

    @property
    def is_bind_wechat(self):
        return self.get_props_item("is_bind_wechat") or 0

    @property
    def is_bind_weibo(self):
        return self.get_props_item("is_bind_weibo") or 0

    @property
    def localtime(self):
        return timezone.localtime(self.last_login)

    @property
    def natural_time(self):
        return time_format(self.localtime)

    def _get_last_pa_time(self):
        return self.get_props_item("last_pa_time")

    def _set_last_pa_time(self, value):
        return self.set_props_item("last_pa_time", value)

    last_pa_time = property(_get_last_pa_time, _set_last_pa_time)

    def _get_gift_count(self):
        return self.get_props_item("gift_count") or 0

    def _set_gift_count(self, value):
        return self.set_props_item("gift_count", value)

    gift_count = property(_get_gift_count, _set_gift_count)

    def _get_paing(self):
        return self.get_props_item("paing") or 0

    def _set_ping(self, value):
        return self.set_props_item("paing", value)

    paing = property(_get_paing, _set_ping)

    @property
    def avatar_url(self):
        if ".jpg" in self.avatar:
            return "%s/%s@base@tag=imgScale&w=150&h=150" % (settings.AVATAR_BASE_URL, self.avatar)

        if self.id < 170104:
            if self.avatar:
                return "http://img.gouhuoapp.com/%s?imageView2/1/w/150/h/150/format/jpg/q/80" % self.avatar

        return "%s/default_avatar@base@tag=imgScale&w=150&h=150" % (settings.AVATAR_BASE_URL)

    @property
    def disable_login(self):
        banuser = BanUser.objects.filter(user_id=self.id).first()
        if banuser:
            if banuser.second == 0:
                return True

            dtime = banuser.date + timedelta(seconds=banuser.second)
            if timezone.now() < dtime:
                return True
        return False

    def create_rong_token(self):
        from corelib.rong import client
        res = client.user_get_token(str(self.id), self.nickname, self.avatar_url)
        return res['token']

    def check_friend_relation(self, user_id):
        from .friend import Friend, InviteFriend
        is_friend = Friend.is_friend(owner_id=self.id, friend_id=user_id)
        if is_friend:
            return UserEnum.friend.value
        elif InviteFriend.is_invited_user(user_id=self.id, friend_id=user_id):
            return UserEnum.be_invite.value
        elif InviteFriend.is_invite_user(user_id=self.id, friend_id=user_id):
            return UserEnum.invite.value
        return UserEnum.nothing.value

    @property
    def is_paid(self):
        return self.paid == str(self.id)

    def push_role(self, friend_id):
        no_push_ids = redis.hkeys(REDIS_NO_PUSH_IDS % self.id)
        if friend_id.encode() in no_push_ids:
            return False
        return True

    def basic_info(self, user_id=None):
        nickname = "" if self.nickname is None else self.nickname,
        return {
            "id": self.id,
            "display_nickname": nickname,
            "nickname": nickname,
            "avatar_url": self.avatar_url,
            "gender": self.gender,
            "intro": self.intro or "",
            "paid": str(self.paid),
            "is_paid": self.is_paid,
            "is_contact": self.is_contact
        }

    def detail_info(self, user_id=None):
        from .friend import common_friends, Friend
        detail_info = self.basic_info()
        if user_id:
            friend = Friend.objects.filter(user_id=user_id, friend_id=self.id).first()
            if friend:
                detail_info["is_invisible"] = friend.invisible
                detail_info["is_push"] = friend.push
                detail_info["user_relation"] = UserEnum.friend.value
            else:
                detail_info["user_relation"] = self.check_friend_relation(user_id=user_id)
                detail_info["gift_count"] = self.gift_count
                common_friends = common_friends(user_id=user_id, to_user_id=self.id)
                common_friend_str = ",".join(common_friends)
                detail_info["common_friends"] = common_friend_str or ""
                detail_info["is_paid"] = self.is_paid
                detail_info["is_bind_wechat"] = self.is_bind_wechat or 0
                detail_info["is_bind_weibo"] = self.is_bind_weibo or 0

            place = Place.get(user_id=self.id)
            if place:
                dis = place.get_dis(to_user_id=user_id)
                if dis:
                    detail_info["location"] = u"%s公里" % dis
            return detail_info

        else:
            detail_info["gift_count"] = self.gift_count
            detail_info["is_paid"] = self.is_paid
            detail_info["is_bind_wechat"] = self.is_bind_wechat or 0
            detail_info["is_bind_weibo"] = self.is_bind_weibo or 0

            return detail_info

auth_models.User = User


class ThirdUser(models.Model):
    mobile = models.CharField(max_length=20, db_index=True, default=0)
    third_id = models.CharField(max_length=30)
    third_name = models.CharField(max_length=20)

    class Meta:
        db_table = "third_user"


class TempThirdUser(models.Model):
    third_id = models.CharField(max_length=30)
    third_name = models.CharField(max_length=20)
    gender = models.SmallIntegerField(default=0)
    nickname = models.CharField(max_length=50)
    avatar = models.CharField(max_length=255)
    wx_unionid = models.CharField(max_length=50, default="")
    user_id = models.IntegerField(default=0)

    class Meta:
        db_table = "temp_third_user"


class BanUser(models.Model):
    user_id = models.IntegerField()
    desc = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    second = models.IntegerField()

    class Meta:
        db_table = "ban_user"

    @classmethod
    def add(cls, user_id, second):
        cls.objects.create(user_id=user_id, second=second)

    def get(cls, id):
        return cls.objects.filter(id=id).first()


def fuck_you(user_id):
    import hashlib
    from corelib.rongcloud import RongCloud
    user = User.get(user_id)
    sign = hashlib.sha1(user.rong_token.encode()).hexdigest()
    data = {
        "type": 4444,
        "data": {
            "sign": sign
        }
    }
    RongCloud().send_hide_message(user_id, user_id, data)


@receiver(post_save, sender=ThirdUser)
def add_thirduser_after(sender, created, instance, **kwargs):
    if created:
        user = User.objects.filter(mobile=instance.mobile).first()
        if instance.third_name == "wx":
            user.set_props_item("is_bind_wechat", 1)
        elif instance.third_name == "wb":
            user.set_props_item("is_bind_weibo", 1)


@receiver(post_delete, sender=ThirdUser)
def del_thirduser_after(sender, instance, **kwargs):
    user = User.objects.filter(mobile=instance.mobile).first()
    if instance.third_name == "wx":
        user.set_props_item("is_bind_wechat", 0)
    elif instance.third_name == "wb":
        user.set_props_item("is_bind_weibo", 0)


@receiver(post_save, sender=User)
def save_user_after(sender, created, instance, **kwargs):
    redis.delete(MC_USER_KEY % instance.id)


@receiver(post_delete, sender=User)
def delele_user_after(sender, instance, **kwargs):
    redis.delete(MC_USER_KEY % instance.id)
