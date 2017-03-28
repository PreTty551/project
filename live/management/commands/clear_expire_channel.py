# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import time

from corelib.redis_store import redis

from livemedia.models import Channel, ChannelMember


CHANNEL_EXPIRE_TIME = 120


class Command(BaseCommand):
    help = u'清理过期房间'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        closed_channels = redis.zrange("amumu:socket:closed_clients", 0, -1, withscores=True)
        for user_id, score in closed_channels:
            # 过期
            if (int(time.time()) - CHANNEL_EXPIRE_TIME) > score:
                member = ChannelMember.objects.filter(user_id=user_id).first()
                if member:
                    member.delete()
                redis.zrem("amumu:socket:closed_clients", user_id)
            else:
                break
