# -*- coding: utf-8 -*-
from django.db import models, transaction

from corelib.utils import natural_time


class Firend(models.Model):
    user_id = models.IntegerField()
    firend_id = models.IntegerField()
    status = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def relation(self):
        if self.status == 2:
            return "好友"
        elif self.status == 1:
            return "firend follow me"
        elif self.status == 0:
            return "me follow firend"
        elif self.status == 3:
            return "ignore"

    @transaction.atomic()
    @classmethod
    def invite(cls, user_id, firend_id):
        cls.objects.create(user_id=user_id, firend_id=firend_id, status=F_INVITE)
        cls.objects.create(user_id=firend_id, firend_id=user_id, status=F_BE_INVITE)
        return True

    @transaction.atomic()
    @classmethod
    def agree(cls, user_id, firend_id):
        cls.objects.update(user_id=user_id, firend_id=firend_id, status=F_FIREND)
        cls.objects.update(user_id=firend_id, firend_id=user_id, status=F_FIREND)
        return True

    def ignore(self):
        self.status = F_IGNORE
        self.save()
        return True

    @property
    def localtime(self):
        return timezone.localtime(self.date)

    @property
    def natural_time(self):
        return time_format(self.localtime)

    def invite_count(cls, owner_id):
        return cls.objects.filter(user_id=owner_id, status=F_BE_INVITE).count()

    @classmethod
    def get_firends(cls, owner_id):
        return list(cls.objects.filter(user_id=owner_id, status=F_FIREND))

    @classmethod
    def get_apply_firends(cls, owner_id):
        return list(cls.objects.filter(user_id=owner_id, status=F_BE_INVITE))

    def to_dict(self):
        user = User.get(self.user_id)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nickname": user.nickname,
            "status": self.status,
        }
