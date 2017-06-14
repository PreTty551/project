import json

from enum import Enum, unique
from django.db import models


LogCategory = Enum("Category", ("user", "channel"))


@unique
class ChannelLogType(Enum):
    quit_channel = 1
    kill_app = 2
    agora_offline = 3
    delete_channel = 4


class Logs(models.Model):
    user_id = models.IntegerField()
    type = models.SmallIntegerField()
    category = models.SmallIntegerField()
    extras = models.CharField(max_length=255, default="")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "logs"

    @classmethod
    def add(cls, user_id, type, category, extras):
        return cls.objects.create(user_id=user_id,
                                  type=type,
                                  category=category,
                                  extras=json.dumps(extras))
