# -*- coding: utf-8 -*-
from enum import Enum, unique

from django.db import models, transaction


@unique
class IgnoreType(Enum):
    CONTACT_IN_APP = 1
    CONTACT_OUT_APP = 2
    DEGREE_FIREND = 3


class Ignore(models.Model):
    owner_id = models.IntegerField()
    user_id = models.IntegerField()
    type = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def add(cls, owner_id, user_id, type):
        return cls.objects.filter(owner_id=owner_id, user_id=user_id, type=type)

    @classmethod
    def get_degree_friends(cls, owner_id):
        return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.DEGREE_FIREND.value)
                               .values_list("user_id", flat=True))

    @classmethod
    def get_contacts_in_app(cls, owner_id):
        return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.CONTACT_IN_APP.value)
                               .values_list("user_id", flat=True))

    @classmethod
    def get_contacts_out_app(cls, owner_id):
        return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.CONTACT_OUT_APP.value)
                               .values_list("user_id", flat=True))
