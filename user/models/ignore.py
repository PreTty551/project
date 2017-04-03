# -*- coding: utf-8 -*-
from enum import Enum, unique

from django.db import models, transaction


@unique
class IgnoreType(Enum):
    CONTACT_IN_SAY = 1
    CONTACT_OUT_SAY = 2
    DEGREE_FIREND = 3


class Ignore(models.Model):
    owner_id = models.IntegerField()
    user_id = models.IntegerField()
    type = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    # @classmethod
    # def get_invite_firends(cls, owner_id):
    #     return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.INVITE_FIREND.value)
    #                            .values_list("user_id", flat=True))
    #
    # @classmethod
    # def get_agree_firends(cls, owner_id):
    #     return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.AGREE_FIREND.value)
    #                            .values_list("user_id", flat=True))
    #
    # @classmethod
    # def get_invite_contacts(cls, owner_id):
    #     return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.INVITE_CONTACT.value)
    #                            .values_list("user_id", flat=True))

    @classmethod
    def get_degree_firends(cls, owner_id):
        return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.DEGREE_FIREND.value)
                               .values_list("user_id", flat=True))

    @classmethod
    def get_contacts_in_say(cls, owner_id):
        return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.CONTACT_IN_SAY.value)
                               .values_list("user_id", flat=True))

    @classmethod
    def get_contacts_out_say(cls, owner_id):
        return list(cls.objects.filter(owner_id=owner_id, type=IgnoreType.CONTACT_OUT_SAY.value)
                               .values_list("user_id", flat=True))
