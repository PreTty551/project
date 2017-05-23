from django.core.management.base import BaseCommand
import time
import datetime

from corelib.redis import redis
from corelib.agora import Agora

from user.models import User
from live.models import Channel, ChannelMember


class Command(BaseCommand):
    help = u'清理过期房间'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        members = ChannelMember.objects.all()
        for member in members:
            agora = Agora(member.user_id)
            is_online = agora.query_online()
            if not is_online:
                ChannelMember.objects.filter(user_id=member.user_id).delete()
                user = User.get(member.user_id)
                user.last_pa_time = time.time()
                user.paing = 0
                print("clear user: %s, date: %s" % (member.user_id, datetime.datetime.now()))
