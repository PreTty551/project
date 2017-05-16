# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ida.models import Duty, duty_user_live_time


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        duty_ids = list(Duty.objects.filter(group="黑白校园").values_list("user_id", flat=True))
        today_str = datetime.datetime.strftime(timezone.now(), "%Y-%m-%d")
        end = datetime.datetime.strptime(today_str, '%Y-%m-%d')
        start = start + datetime.timedelta(days=-1)
        duty_user_live_time(duty_user_add_friend, 1, start, end)
