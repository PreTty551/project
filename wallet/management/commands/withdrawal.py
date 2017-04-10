# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from wallet.models import Withdrawals


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Withdrawals.withdrawal()
