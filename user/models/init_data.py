import os
import sys
import random

from xpinyin import Pinyin

from django.db import connection, connections

from .user import User, TempThirdUser, ThirdUser
from .friend import InviteFriend, Friend
from .contact import UserContact
from wallet.models import Wallet


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
    Gift.objects.create(id=1, name="拍巴掌", amount=11, size="m", icon="1", order=1, message="送给 %s 拍巴掌")
    Gift.objects.create(id=2, name="比心心", amount=111, size="m", icon="2", order=2, message="送给 %s 比心心")
    Gift.objects.create(id=3, name="甜甜圈", amount=233, size="m", icon="3", order=3, message="送给 %s 甜甜圈")
    Gift.objects.create(id=4, name="么么哒", amount=419, size="m", icon="4", order=4, message="送给 %s 么么哒")
    Gift.objects.create(id=5, name="666", amount=666, size="m", icon="5", order=5, message="送给 %s 666")
    Gift.objects.create(id=6, name="鸡年大吉", amount=888, size="m", icon="6", order=6, message="送给 %s 鸡年大吉")
    Gift.objects.create(id=7, name="熊宝宝", amount=1999, size="m", icon="7", order=7, message="送给 %s 熊宝宝")
    Gift.objects.create(id=8, name="宝石皇冠", amount=6666, size="l", icon="8", order=8, message="送给 %s 宝石皇冠")
    Gift.objects.create(id=9, name="啤酒", amount=233, size="m", icon="9", order=9, message="送给 %s 啤酒")


def import_user():
    with connections["gouhuo"].cursor() as cursor:
        cursor.execute("SELECT * FROM ogow_user where from_to!='douban'")
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
            mobile = row[11]
            if mobile == "undefined":
                mobile = row[0]
            user.mobile = mobile if mobile else row[0]
            nickname = row[12]
            user.nickname = nickname[:50]
            avatar = row[13]
            user.avatar = avatar[:40]
            user.gender = row[14]
            intro = row[16] or ""
            user.intro = intro if len(intro) <= 25 else ""
            user.country = ""
            user.country_code = "86"
            user.is_contact = False
            user.platform = 0
            user.version = ""
            user.paid = row[0]
            # user.set_password(user.username)

            pinyin = Pinyin().get_pinyin(user.nickname, "")
            user.pinyin = pinyin[:50]
            try:
                user.save()
            except IntegrityError:
                user.mobile = row[0]
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
        follow_ids = [str(c[0]) for c in cursor.fetchall() if User.objects.filter(id=c[0]).first()]
        if not follow_ids:
            continue

        str_follow_ids = ",".join(follow_ids)
        sql = "SELECT user_id FROM yi_followuser where followed_user_id=%s and user_id in (%s)" % (user_id, str_follow_ids)
        cursor.execute(sql)
        fans_ids = [str(r[0]) for r in cursor.fetchall() if User.objects.filter(id=r[0]).first()]
        if not fans_ids:
            continue

        for fans_id in fans_ids:
            Friend.objects.create(user_id=user_id, friend_id=fans_id)
            InviteFriend.objects.filter(user_id=user_id, invited_id=fans_id).delete()
            InviteFriend.objects.filter(invited_id=fans_id, user_id=user_id).delete()

        invited_ids = set(follow_ids) ^ set(fans_ids)
        for invited_id in invited_ids:
            InviteFriend.objects.create(user_id=user_id, invited_id=invited_id, status=10)


def import_account():
    cursor = connections['gouhuo'].cursor()
    cursor.execute("SELECT user_id, amount FROM user_account")
    for row in cursor.fetchall():
        Wallet.objects.create(user_id=row[0], amount=row[1])


def import_order():
    cursor = connections['gouhuo'].cursor()
    for w in Wallet.objects.all():
        cursor.execute("SELECT count(1) FROM account_order where answer_id=0 and to_user_id=%s" % w.user_id)
        r = cursor.fetchone()
        user = User.get(u.user_id)
        if not user:
            continue

        user.gift_count = r[0]


def run():
    init_gift()
    import_user()
    import_thirduser()
    import_friend()
    import_account()
    # 礼物数
