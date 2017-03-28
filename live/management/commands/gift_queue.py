# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import json
import time

from corelib.redis import redis
from corelib.agora import Agora


class Command(BaseCommand):
    help = u'房间礼物队列'

    def add_arguments(self, parser):
        parser.add_argument('channel_id', type=int)

    def handle(self, *args, **options):
        ps = redis.pubsub()
        channel_id = options["channel_id"]
        redis.delete("channel:%s:gitf_queue" % channel_id)
        ps.subscribe("sub:channel:%s" % channel_id)

        for item in ps.listen():
            if item["type"] == 'message':
                gift = redis.lpop("channel:%s:gitf_queue" % channel_id)
                if gift:
                    data = json.loads(gift)
                    agora = Agora(user_id=data["from"])
                    agora.send_cannel_msg(channel_id=channel_id, **data)
                    time.sleep(2)
