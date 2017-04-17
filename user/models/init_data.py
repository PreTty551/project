import os
import sys
import random

from xpinyin import Pinyin

from django.db import connection, connections

from .user import User, TempThirdUser, ThirdUser
from .friend import InviteFriend, Friend
from .contact import UserContact


def init_data(user_id=None):
    for i in range(0, 50):
        User.objects.add_user(nickname="test%s" % i, mobile=18800000000 + i)

    for user in User.objects.all():
        for invite_user in User.objects.all():
            InviteFriend.add(user_id=user.id, invited_id=invite_user.id)

        for invite in InviteFriend.objects.all()[:25]:
            InviteFriend.agree(invite.user_id, invite.invited_id)


def init_data_to_user(user_id):
    for i in range(10, 20):
        UserContact.objects.create(user_id=user_id, name="test%s" % i, mobile=18800000000 + i)
        User.objects.add_user(nickname="test%s" % i, mobile=18800000000 + i)

    for j in range(11, 22):
        UserContact.objects.create(user_id=user_id, name="test%s" % j, mobile=18800000000 + j)

    for user in User.objects.exclude(id=user_id):
        InviteFriend.add(user_id=user.id, invited_id=user_id)


def init_gift():
    from gift.models import Gift
    Gift.objects.create(id=1, name="拍巴掌", amount=1, size="m", icon="1", order=1, message="送给 %s 拍巴掌")
    Gift.objects.create(id=2, name="比心心", amount=1, size="m", icon="2", order=2, message="送给 %s 比心心")
    Gift.objects.create(id=3, name="甜甜圈", amount=1, size="m", icon="3", order=3, message="送给 %s 甜甜圈")
    Gift.objects.create(id=4, name="么么哒", amount=1, size="m", icon="4", order=4, message="送给 %s 么么哒")
    Gift.objects.create(id=5, name="666", amount=1, size="m", icon="5", order=5, message="送给 %s 666")
    Gift.objects.create(id=6, name="鸡年大吉", amount=1, size="m", icon="6", order=6, message="送给 %s 鸡年大吉")
    Gift.objects.create(id=7, name="熊宝宝", amount=1, size="m", icon="7", order=7, message="送给 %s 熊宝宝")
    Gift.objects.create(id=8, name="宝石皇冠", amount=1, size="l", icon="8", order=8, message="送给 %s 宝石皇冠")


def import_user():
    with connections["gouhuo"].cursor() as cursor:
        cursor.execute("SELECT * FROM ogow_user where from_to='yi'")
        for row in cursor.fetchall():
            user = User()
            user.id = row[0]
            user.password = row[1]
            user.last_login = row[2]
            user.is_superuser = row[3]
            user.username = row[4]
            user.first_name = row[5]
            user.last_name = row[6]
            user.email = row[7]
            user.is_staff = row[8]
            user.is_active = row[9]
            user.date_joined = row[10]
            user.mobile = row[11]
            user.nickname = row[12]
            avatar = row[13]
            user.avatar = avatar[:20] if len(avatar) > 19 else avatar
            user.gender = row[14]
            user.intro = row[16] or ""
            user.country = ""
            user.country_code = "86"
            user.is_import_contact = False
            user.platform = 0
            user.version = ""

            pinyin = Pinyin().get_pinyin(user.nickname, "")
            user.pinyin = pinyin[:30]
            user.save()


def import_thirduser():
    cursor = connections['gouhuo'].cursor()
    cursor1 = connections['gouhuo'].cursor()

    cursor.execute("SELECT * FROM ogow_thirduserid")
    for row in cursor.fetchall():
        cursor1.execute("SELECT nickname, gender FROM ogow_user where id=%s" % row[2])
        r = cursor1.fetchone()
        if not r:
            continue

        nickname = r[0] if r else ""
        platform = int(row[3])
        if platform == 1:
            ttu = TempThirdUser()
            ttu.mobile = ""
            ttu.avatar = ""
            ttu.third_id = row[4] if int(row[3]) == 1 else row[1]
            ttu.third_name = "wx"
            ttu.wx_unionid = row[1].replace("wx_", "")
            ttu.nickname = nickname[:20]
            ttu.user_id = row[2]
            ttu.gender = r[1]
            ttu.save()
        elif platform == 2:
            ttu = TempThirdUser()
            ttu.mobile = ""
            ttu.avatar = ""
            ttu.third_id = row[1].replace("wb_", "")
            ttu.third_name = "wb"
            ttu.wx_unionid = ""
            ttu.nickname = nickname[:20]
            ttu.user_id = row[2]
            ttu.gender = r[1]
            ttu.save()


def import_friend():
    user_ids = User.objects.values_list("id", flat=True)
    cursor = connections['gouhuo'].cursor()
    for user_id in user_ids:
        cursor.execute("SELECT followed_user_id FROM yi_followuser where user_id=%s" % user_id)
        follow_ids = [c[0] for c in cursor.fetchall()]
        sql = "SELECT user_id FROM yi_followuser where followed_user_id=%s and user_id in %s" % (user_id, tuple(follow_ids))
        cursor.execute(sql)
        for r in cursor.fetchall():
            Friend.add(user_id=user_id, friend_id=r[0])
