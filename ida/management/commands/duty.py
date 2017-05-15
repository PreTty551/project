# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from ida.models import Duty


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # for gid in range(1, 4):
        #     duty_ids = list(Duty.objects.filter(group=gid).values_list("user_id", flat=True))
        #     duty_user(duty_ids, gid)

        DD = "2017-05-14 00:00:00"
        aaa = """170418
170419
170440
170416
170409
170425
170430
170417
170415
170427
170407
170408
170442
170414
170447
170510
170568
170613
170589
170747
170756
170439
170785
"""
        user_ids = [user_id for user_id in aaa.split("\n") if user_id]
        start = datetime.datetime.strptime(DD, '%Y-%m-%d %H:%M:%S')
        end = start + datetime.timedelta(days=1)
        duty_user(user_ids, 1, start, end)

        bbb = """170504
170325
170388
170480
170375
170352
170343
170396
170522
170326
170337
170395
170509
170539
170448
170398
170378
170648
170504
170342
170674
170646
170356
170810
170716
170764
170388
170805
170760
170741
170739
170691
170457
170615
170809
170748
170725
170714
170740
170664
170824
170900
170901"""
        user_ids = [user_id for user_id in bbb.split("\n") if user_id]
        start = datetime.datetime.strptime(DD, '%Y-%m-%d %H:%M:%S')
        end = start + datetime.timedelta(days=1)
        duty_user(user_ids, 2, start, end)
