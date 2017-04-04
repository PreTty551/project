# -*- coding: utf-8 -*-
from django.db import models, transaction

from corelib.utils import natural_time
from user.models import User


class InviteFirend(models.Model):
    user_id = models.IntegerField()
    invited_id = models.IntegerField()
    status = models.SmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def add(cls, user_id, invited_id):
        return cls.objects.create(user_id=user_id, invited_id=invited_id)

    @classmethod
    def agree(cls, user_id, invited_id):
        cls.objects.filter(user_id=user_id, invited_id=invited_id).update(status=1)
        Firend.add(user_id=user_id, firend_id=invited_id)

    @classmethod
    def ignore(cls, id):
        cls.objects.filter(id=id).update(status=2)

    @classmethod
    def count(cls, user_id):
        return cls.objects.filter(invited_id=user_id).count()

    @classmethod
    def get_add_firend_request_list(cls, user_id):
        return list(cls.objects.filter(firend_id=user_id, status=0).values_list("user_id", flat=True))


class Firend(models.Model):
    user_id = models.IntegerField()
    firend_id = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    @transaction.atomic()
    def add(cls, user_id, firend_id):
        Firend.objects.create(user_id=user_id, firend_id=firend_id)
        Firend.objects.create(user_id=firend_id, firend_id=user_id)
        return True

    @property
    def localtime(self):
        return timezone.localtime(self.date)

    @property
    def natural_time(self):
        return time_format(self.localtime)

    @classmethod
    @transaction.atomic()
    def cancel(cls, user_id, firend_id):
        cls.objects.filter(user_id=user_id, firend_id=firend_id).delete()
        cls.objects.filter(user_id=firend_id, firend_id=user_id).delete()
        return True

    @classmethod
    def get_firend_ids(cls, user_id):
        return list(cls.objects.filter(user_id=user_id).values_list("firend_id", flat=True))

    @classmethod
    def is_invited_user(cls, user_id, firend_id):
        return True if cls.objects.filter(user_id=firend_id, firend_id=user_id).first() else False

    def to_dict(self):
        user = User.get(self.user_id)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nickname": user.nickname,
            "status": self.status,
        }


def two_degree_relation(user_id):
    firend_ids = list(Firend.objects.filter(user_id=user_id)
                                    .values_list("firend_id", flat=True))
    second_firend_list = list(Firend.objects.filter(user_id__in=firend_ids)
                                            .exclude(firend_id=user_id)
                                            .values_list("user_id", "firend_id"))

    obj = []
    for second_firend in second_firend_list:
        obj.append((second_firend[0], second_firend[1]))

    _dict = {}
    for uid, fid in obj:
        _ = _dict.setdefault(fid, [])
        _.append(uid)

    result = []
    for user_id, mutual_firend_ids in _dict.items():
        user = User.get(id=user_id)
        basic_info = user.basic_info()
        mutual_firend = [User.get(firend_id).nickname for firend_id in mutual_firend_ids]
        basic_info["mutual_firend"] = mutual_firend
        result.append(basic_info)
    return result
