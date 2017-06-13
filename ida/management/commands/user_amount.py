# -*- coding: utf-8 -*-
import time
import datetime
import pytz

from django.core.management.base import BaseCommand
from django.utils import timezone

from corelib.redis import redis
from corelib.utils import random_str

from user.models import User, Friend, UserDynamic
from user.consts import REDIS_FRIEND_DATE
from live.models import LiveMediaLog
from wallet.models import *


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        start = '2017-06-11'
        end = '2017-06-12'

        user_list = [(157123, '2017-06-08'), (167659, '2017-06-08'), (174136, '2017-06-08'), (89348, '2017-06-08'), \
                    (173935, '2017-06-08'), (183067, '2017-06-10'), (81402, '2017-06-10'), (182941, '2017-06-10'), \
                    (167, '2017-06-10'), (181621, '2017-06-10'), (172024, '2017-06-10'), \
                    (246, '2017-06-10'), (182706, '2017-06-10'), (544, '2017-06-10')]

        for user_id, create_date in user_list:
            print("user_id=",user_id)
            # 查询这个人所有的好友
            friend_ids = Friend.objects.filter(friend_id=user_id, date__gte=create_date) \
                                       .values_list("user_id", flat=True)

            time_uids = []
            # 所有有好友的人
            for friend_id in friend_ids:
                f = Friend.objects.filter(user_id=friend_id).first()
                if f.friend_id == user_id:
                    time_uids.append(friend_id)


            z_time = []
            moneys = {}
            amount = 0
            for time_uid in time_uids:
                logs = LiveMediaLog.objects.filter(user_id=time_uid, date__gte=start, end_date__lt=end)
                seconds = 0
                for log in logs:
                    seconds += (log.end_date - log.date).seconds

                if seconds == 0:
                    continue

                m = seconds // 60
                if (m >= 10):
                    amount += 10
                elif m:
                    amount += m

                #moneys[time_uid] = money
                z_time.append(seconds // 60)

            """
            out_trade_no = random_str()
            WalletRecharge.objects.create(user_id=user_id,
                                          out_trade_no=out_trade_no,
                                          amount=amount * 100)
            WalletRecharge.recharge_callback(out_trade_no=out_trade_no, category=4)
            """
            print(z_time)
            print("time_uids", time_uids)
            print("amount=",amount)