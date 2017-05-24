import copy
import datetime

from django.db import models
from django.utils import timezone

from user.models import User, Friend, ChannelAddFriendLog
from live.consts import ChannelType
from live.models import LiveMediaLog


class Duty(models.Model):
    user_id = models.IntegerField(db_index=True)
    group = models.CharField(max_length=50, default="", blank=True)
    memo = models.CharField(max_length=255, default="", blank=True)


def duty_user_add_friend(user_ids, group, start_date, end_date):
    public_party_ids = []
    friend_party_ids = []

    table_title = "值班人ID,昵称,朋友总数,好友party,总数,公开party,总数\n"
    d = start_date.strftime('%Y-%m-%d')
    f = open("/home/mengwei/duty/duty_g%s_%s.csv" % (group, d), "w+")
    f.writelines(table_title)
    for user_id in user_ids:
        if not user_id:
            continue

        user = User.get(user_id)
        friend_ids = list(Friend.objects.filter(user_id=user_id, date__gte=start_date, date__lt=end_date).values_list("friend_id", flat=True))
        logs = ChannelAddFriendLog.objects.filter(user_id=user_id, date__gte=start_date, date__lt=end_date).values_list("friend_id", "channel_type").distinct()
        for friend_id, channel_type in logs:
            if channel_type == ChannelType.public.value:
                public_party_ids.append(friend_id)
            else:
                friend_party_ids.append(friend_id)

        logs = ChannelAddFriendLog.objects.filter(friend_id=user_id, date__gte=start_date, date__lte=end_date).values_list("user_id", "channel_type").distinct()
        for user_id, channel_type in logs:
            if channel_type == ChannelType.public.value:
                if user_id not in public_party_ids:
                    public_party_ids.append(user_id)
            else:
                if user_id not in friend_party_ids:
                    friend_party_ids.append(user_id)

        public_party_ids = list(set(friend_ids) & set(public_party_ids))
        friend_party_ids = list(set(friend_ids) & set(friend_party_ids))
        public_party_ids = [str(uid) for uid in public_party_ids]
        friend_party_ids = [str(uid) for uid in friend_party_ids]

        data = [str(user.id), user.nickname, str(len(friend_ids)),
                " ".join(friend_party_ids), str(len(friend_party_ids)),
                " ".join(public_party_ids), str(len(public_party_ids))]
        f.write(",".join(data) + "\n")

    f.close()


def duty_user_live_time(user_ids, group, start_date, end_date):
    public_party_ids = []
    friend_party_ids = []

    table_title = "值班人ID,昵称,开始时间,结束时间,房间类型\n"
    for user_id in user_ids:
        if not user_id:
            continue

        f = open("/home/mengwei/duty/duty_live_%s.csv" % user_id, "w")
        f.writelines(table_title)

        user = User.get(user_id)
        logs = LiveMediaLog.objects.filter(user_id=user_id,
                                           type=1,
                                           status=2,
                                           date__gte=start_date,
                                           date__lt=end_date)
        for log in logs:
            start_str = datetime.datetime.strftime(timezone.localtime(log.date), "%Y-%m-%d %H:%M:%S")
            end_str = datetime.datetime.strftime(timezone.localtime(log.end_date), "%Y-%m-%d %H:%M:%S")
            data = [str(log.user_id), user.nickname, start_str, end_str, str(log.channel_type)]
            f.write(",".join(data) + "\n")

        f.close()


def duty_user_live_time_week(user_ids, group, start_date):
    public_party_ids = []
    friend_party_ids = []

    table_title = "值班人ID,昵称,周一,周二,周三,周四,周五,周六,周日\n"
    f = open("/home/mengwei/duty/duty_live_week.csv", "w")
    f.writelines(table_title)

    for user_id in user_ids:
        if not user_id:
            continue

        user = User.get(user_id)

        data = []
        data.append(str(user_id))
        data.append(user.nickname)

        start = copy.deepcopy(start_date)
        for i in list(range(1, 8)):
            end_date = start + datetime.timedelta(days=1)
            logs = LiveMediaLog.objects.filter(user_id=user_id,
                                               type=1,
                                               status=2,
                                               date__gte=start,
                                               date__lt=end_date)

            seconds = 0
            for log in logs:
                seconds += (log.end_date - log.date).seconds
            data.append(str(seconds // 60))
            start = end_date
        f.write(",".join(data) + "\n")

    f.close()


def duty_party_time(user_ids, start_date, days):
    result = []
    for user_id in user_ids:
        if not user_id:
            continue

        user = User.get(user_id)
        if not user:
            continue

        data = []
        data.append(str(user_id))
        data.append(user.nickname)

        start = copy.deepcopy(start_date)
        for i in list(range(1, int(days))):
            end_date = start + datetime.timedelta(days=1)
            logs = LiveMediaLog.objects.filter(user_id=user_id,
                                               type=1,
                                               status=2,
                                               date__gte=start,
                                               date__lt=end_date)

            seconds = 0
            for log in logs:
                seconds += (log.end_date - log.date).seconds
            data.append(str(seconds // 60))
            start = end_date
        result.append(data)
    return result
