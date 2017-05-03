# -*- coding: utf-8 -*-
from enum import Enum, unique

from django.db import models, transaction


@unique
class IgnoreType(Enum):
    KNOW_USER = 1


class Ignore(models.Model):
    owner_id = models.IntegerField()
    ignore_id = models.IntegerField()
    ignore_type = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def add(cls, owner_id, ignore_id, ignore_type):
        return cls.objects.create(owner_id=owner_id, ignore_id=ignore_id, ignore_type=ignore_type)
