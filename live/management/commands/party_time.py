# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand
from livemedia.models import LiveMediaLog


class Command(BaseCommand):
    help = u'房间礼物队列'

    def add_arguments(self, parser):
        parser.add_argument('channel_id', type=int)

    def handle(self, *args, **options):
        min_time = "2017-03-05 16:00:00"
        max_time = "2017-03-06 16:00:00"

        min_date = datetime.datetime.strptime(min_time, '%Y-%m-%d %H:%M:%S')
        max_date = datetime.datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')

        today = datetime.datetime.now()
        days = (today - min_date).days

        for day in range(days):
            min_date = min_date + datetime.timedelta(day)
            max_date = max_date + datetime.timedelta(day)

            party_user_ids = list(LiveMediaLog.objects.filter(date__gte=min_date, date__lt=max_date)
                                                      .values_list("user_id", flat=True).distinct())

            for user_id in party_user_ids:
                seconds = 0
                add_channel_log = LiveMediaLog.objects.filter(date__gte=min_date, date__lt=max_date, user_id=user_id, status=1).order_by("channel_id")
                quit_channel_log = LiveMediaLog.objects.filter(date__gte=min_date, date__lt=max_date, status=2).order_by("channel_id")
                for add_log in add_channel_log:
                    quit_log = LiveMediaLog.objects.filter(date__gte=min_date, date__lt=max_date, status=2, channel_id=add_log.channel_id, user_id=user_id).order_by("channel_id").first()




                    if not quit_log:
                        print "not id %s", add_log.id

                    if quit_log.date < add_log.date:
                        print "error, %s" % add_log.id
                    seconds += (quit_log.date - add_log.date).seconds

                if seconds / 60 > 20:
                    print ">20, user_id %s %s" % (user_id, seconds / 3600.0)
            break
