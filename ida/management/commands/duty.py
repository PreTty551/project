# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from ida.models import Duty, duty_user_add_friend


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        duty_ids = list(Duty.objects.filter(group="黑白校园").values_list("user_id", flat=True))
        today_str = datetime.datetime.strftime(timezone.now(), "%Y-%m-%d")
        for i in list(range(15, 22)):
            start = datetime.datetime.strptime("2017-05-%s" % i, '%Y-%m-%d')
            end = start + datetime.timedelta(days=1)
            duty_user_add_friend(duty_ids, 1, start, end)
