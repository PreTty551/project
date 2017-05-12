# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ida.models import Duty


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for gid in range(1, 4):
            duty_ids = list(Duty.objects.filter(group=gid).values_list("user_id", flat=True))
            duty_user(duty_ids, gid)
