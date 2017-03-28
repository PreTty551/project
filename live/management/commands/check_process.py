# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import subprocess

from corelib.store import mc
from livemedia.models import Channel


class Command(BaseCommand):
    help = u'检查礼物队列和socket是否存在'

    def add_arguments(self, parser):
        pass

    def socket_server_exist(self):
        pass

    def handle(self, *args, **options):
        channels = Channel.objects.all()
        for channel in channels:
            p = subprocess.Popen(["kill", "-0", str(channel.pid)])
            if p.wait() == 0:
                mc.set("channel:%s:gift_switch" % channel.channel_id, 1, 120)
            else:
                subprocess.Popen(["python", "manage.py", "gift_queue", str(channel.channel_id)])
