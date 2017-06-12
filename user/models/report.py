from django.db import models


class UserReport(models.Model):
    user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    type = models.SmallIntegerField()
    date = models.DateTimeField('date', auto_now_add=True)

    class Meta:
        db_table = "user_report"
