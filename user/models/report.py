import datetime

from django.db import models


class UserReport(models.Model):
    user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    type = models.SmallIntegerField()
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        db_table = "user_report"


class SpecialReportUser(models.Model):
    """特殊的举报用户"""
    user_id = models.IntegerField()
    date = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = "special_report_user"
