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
        friends = Friend.objects.filter(user_id=3)
        for friend in friends:
            user = User.get(friend.friend_id)
            is_paing = user.is_paing
            last_pa_time = user.last_pa_time

            UserDynamic.objects.create(user_id=user.id,
                                       nickname=user.nickname,
                                       avatar=user.avatar,
                                       is_paing=is_paing,
                                       last_pa_time=last_pa_time,
                                       update_date=timezone.now())

            add_friend_time = time.mktime(friend.date.timetuple())
            redis.hset(REDIS_FRIEND_DATE % 3, friend.id, add_friend_time)
