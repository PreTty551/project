# -*- coding: utf-8 -*-
import uuid
import random
import datetime

from itertools import permutations
from xpinyin import Pinyin

from django.utils import timezone
from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager

# from corelib.memcache import mc, cache
from corelib.qiniucloud import Qiniu
from corelib.props import PropsMixin
from corelib.weibo import Weibo
from corelib.utils import natural_time as time_format
from corelib.mc import cache

from user.consts import UserEnum, MC_USER_KEY, EMOJI_LIST
from .place import Place


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, mobile="", **extra_fields):
        extra_fields.setdefault('nickname', '')
        if not mobile:
            mobile = random.randint(13800000000, 13900000000)
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
            user.save()
            return user
        except Exception as e:
            return None

    def filter_nickname(self, nickname):
        return super(UserManager, self).get_queryset().filter(nickname=nickname).first()


def rename_nickname(nickname):
    """昵称重名后的处理函数,50个emoji选index个的组合"""
    user = User.objects.filter_nickname(nickname=nickname)
    if not user:
        return nickname

    for i in range(50):
        for e in permutations(EMOJI_LIST, i + 1):
            e_str = "".join(e)
            new_nickname = "%s%s" % (nickname, e_str)
            user = User.objects.filter_nickname(nickname=new_nickname)
            if not user:
                return new_nickname


def create_third_user(third_id, third_name, nickname, avatar, gender, mobile, platform, version):
    nickname = nickname.replace(" ", "").replace("#", "").replace("@", "")
    user = User.objects.filter(mobile=mobile).first()
    if not user:
        user = User.objects.add_user(nickname=nickname, gender=gender, mobile=mobile, platform=platform, version=version)
    ThirdUser.objects.create(mobile=mobile, third_id=third_id, third_name=third_name)
    return user


def update_avatar_in_third_login(user_id):
    user = User.get(user_id)
    avatar_url = user.get_props_item("third_user_avatar", "")
    if not avatar_url:
        return

    from corelib.kingsoft.ks3 import KS3
    avatar_name = KS3().fetch_avatar(url=avatar_url, user_id=request.user.id)
    if avatar_name:
        user.avatar = avatar_name
        user.save()


class User(AbstractUser, PropsMixin):
    paid = models.CharField(max_length=50, default="", db_index=True)
    nickname = models.CharField(max_length=30)
    mobile = models.CharField(max_length=20, unique=True, default="")
    avatar = models.CharField(max_length=20, default="")
    gender = models.SmallIntegerField(default=0)
    intro = models.CharField(max_length=100, default="")
    country = models.CharField(max_length=20, default="")
    country_code = models.CharField(max_length=10, default="")
    is_import_contact = models.BooleanField(default=False)
    platform = models.SmallIntegerField(default=0)
    version = models.CharField(max_length=10, default="")
    pinyin = models.CharField(max_length=30, default="")
    online_time = models.DateTimeField(default=timezone.now)
    offline_time = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = u'用户'
        verbose_name_plural = u'用户列表'

    def __getattr__(self, attr):
        try:
            return object.__getattr__(self, attr)
        except AttributeError:
            return ""

    def __str__(self):
        return "<User(id=%s, nickname=%s)>" % (self.id, self.nickname)

    __repr__ = __str__

    @property
    def _props_db_key(self):
        return "db:user:%s" % self.id

    def save(self, *args, **kwargs):
        # mc.delete(MC_USER_KEY % self.id)
        super(User, self).save(*args, **kwargs)

    @classmethod
    @cache("user:%s" % '{id}')
    def get(cls, id):
        return cls.objects.filter(id=id).first()

    def online(self):
        self.online_time = timezone.now()
        self.save()

    def offline(self):
        self.offline_time = timezone.now()
        self.save()

    def is_online(self):
        return True if self.online_time >= self.offline_time else False

    @property
    def localtime(self):
        return timezone.localtime(self.last_login)

    @property
    def natural_time(self):
        return time_format(self.localtime)

    @property
    def avatar_url(self):
        _avatar = "default_avatar"
        if self.avatar:
            _avatar = self.avatar
        else:
            avatar_url = self.get_props_item("third_user_avatar", "")
            if avatar_url:
                return avatar_url
        return "http://img2.gouhuoapp.com/%s?imageView2/1/w/150/h/150/format/jpg/q/80" % _avatar

    @property
    def disable_login(self):
        return self.id in list(BanUser.objects.values_list("user_id", flat=True))

    def rong_token(self):
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
        return UserEnum.nothing.value

    def basic_info(self, user_id=None):
        if user_id:
            memo = Friend.get_memo(user_id=self.id, friend_id=user_id)
        else:
            memo = self.nickname
        return {
            "id": self.id,
            "display_nickname": memo,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "gender": self.gender,
            "intro": self.intro or "",
            "is_import_contact": self.is_import_contact
        }

    def detail_info(self, user_id=None):
        from .friend import common_friend
        common_friends = common_friend(self.id, user_id)
        common_friends = ",".join(common_friends)
        detail_info = self.basic_info()
        detail_info["common_friends"] = common_friends if common_friends else ""
        if user_id:
            detail_info["friend_relation"] = self.check_friend_relation(user_id=user_id)
            place = Place.get(user_id=self.id)
            if place:
                dis = place.get_dis(to_user_id=user_id)
                if dis:
                    detail_info["location"] = u"%s公里" % dis

        return detail_info

auth_models.User = User


class ThirdUser(models.Model):
    mobile = models.CharField(max_length=20, db_index=True, default=0)
    third_id = models.CharField(max_length=30)
    third_name = models.CharField(max_length=20)

    class Meta:
        db_table = "third_user"


class BanUser(models.Model):
    user_id = models.IntegerField()
    desc = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    second = models.IntegerField()

    class Meta:
        db_table = "ban_user"


class TempThirdUser(models.Model):
    third_id = models.CharField(max_length=30)
    third_name = models.CharField(max_length=20)
    gender = models.SmallIntegerField(default=0)
    nickname = models.CharField(max_length=20)
    avatar = models.CharField(max_length=255)
    wx_unionid = models.CharField(max_length=50, default="")
    user_id = models.IntegerField(default=0)

    class Meta:
        db_table = "temp_third_user"


class PokeLog(models.Model):
    user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    status = models.SmallIntegerField()
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        db_table = "poke_log"


def quit_app(user):
    from live.models import ChannelMember
    user.offline()
    ChannelMember.objects.filter(user_id=user.id).delete()
