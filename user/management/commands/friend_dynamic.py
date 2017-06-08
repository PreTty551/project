# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import time

from corelib.store import mc
from live.models import Channel
from user.models import User, Friend, UserDynamic
from user.consts import REDIS_FRIEND_DATE


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        user_ids = list(Friend.objects.values_list("user_id", flat=True).distinct())
        for user_id in user_ids:
            ud = UserDynamic.objects.filter(user_id=user_id).first()
            if ud:
                user = User.get(user_id)
                ud.paing = user.paing
                ud.save()

            user = User.get(user_id)
            is_paing = user.paing or 0
            last_pa_time = user.last_pa_time or None
            if last_pa_time:
                last_pa_time = datetime.datetime.utcfromtimestamp(float(last_pa_time)).replace(tzinfo=pytz.utc)
            else:
                last_pa_time = None

            try:
                if not last_pa_time:
                    UserDynamic.objects.create(user_id=user.id,
                                               nickname=user.nickname,
                                               avatar=user.avatar,
                                               paing=is_paing,
                                               update_date=timezone.now())
                else:
                    UserDynamic.objects.create(user_id=user.id,
                                               nickname=user.nickname,
                                               avatar=user.avatar,
                                               paing=is_paing,
                                               last_pa_time=last_pa_time,
                                               update_date=timezone.now())
            except:
                print("user_id", user_id, user.nickname)

            friends = Friend.objects.filter(user_id=user_id)
            for friend in friends:
                add_friend_time = time.mktime(friend.date.timetuple())
                redis.hset(REDIS_FRIEND_DATE % user_id, friend.id, add_friend_time)
