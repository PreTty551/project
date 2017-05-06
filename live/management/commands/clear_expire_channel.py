from django.core.management.base import BaseCommand
import datetime

from corelib.redis import redis
from corelib.agora import Agora

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
                print("clear user: %s, date: %s" % (member.user_id, datetime.datetime.now()))
