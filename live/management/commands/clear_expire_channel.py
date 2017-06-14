import time
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from corelib.redis import redis
from corelib.agora import Agora

from user.models import User, UserDynamic
from live.models import Channel, ChannelMember


class Command(BaseCommand):
    help = u'清理过期房间'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        d = timezone.now() - datetime.timedelta(seconds=60)
        members = ChannelMember.objects.filter(date__lte=d)
        for member in members:
            agora = Agora(member.user_id)
            is_online = agora.query_online()
            if not is_online:
                ChannelMember.objects.filter(user_id=member.user_id).delete()
                UserDynamic.update_dynamic(user_id=member.user_id, paing=0)
                print("clear user: %s, date: %s" % (member.user_id, datetime.datetime.now()))
