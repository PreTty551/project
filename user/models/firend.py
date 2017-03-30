# -*- coding: utf-8 -*-
from django.db import models, transaction

from corelib.utils import natural_time
from user.models import User
from user.consts import FirendEnum


class Firend(models.Model):
    user_id = models.IntegerField()
    firend_id = models.IntegerField()
    status = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def relation(cls, user_id, firend_id):
        obj = cls.objects.filter(user_id=user_id, firend_id=firend_id).first()
        return obj.status
        if self.status == 2:
            return "好友"
        elif self.status == 1:
            return "firend follow me"
        elif self.status == 0:
            return "me follow firend"
        elif self.status == 3:
            return "ignore"

    # @transaction.atomic()
    @classmethod
    def invite(cls, user_id, firend_id):
        cls.objects.create(user_id=user_id, firend_id=firend_id, status=FirendEnum.invite.value)
        cls.objects.create(user_id=firend_id, firend_id=user_id, status=FirendEnum.be_invite.value)
        return True

    # @transaction.atomic()
    @classmethod
    def agree(cls, user_id, firend_id):
        cls.objects.filter(user_id=user_id, firend_id=firend_id).update(status=FirendEnum.firend.value)
        cls.objects.filter(user_id=firend_id, firend_id=user_id).update(status=FirendEnum.firend.value)
        return True

    def ignore(self):
        self.status = FirendEnum.ignore.value
        self.save()
        return True

    @property
    def localtime(self):
        return timezone.localtime(self.date)

    @property
    def natural_time(self):
        return time_format(self.localtime)

    def invite_count(cls, owner_id):
        return cls.objects.filter(user_id=owner_id, status=FirendEnum.be_invite.value).count()

    @classmethod
    def get_firends(cls, owner_id):
        return list(cls.objects.filter(user_id=owner_id, status=FirendEnum.firend.value))

    @classmethod
    def get_apply_firends(cls, owner_id):
        return list(cls.objects.filter(user_id=owner_id, status=FirendEnum.be_invite.value))

    def to_dict(self):
        user = User.get(self.user_id)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nickname": user.nickname,
            "status": self.status,
        }


def two_degree_relation(user_id):
    firend_ids = list(Firend.objects.filter(user_id=user_id,
                                            status=FirendEnum.firend.value)
                                    .values_list("firend_id", flat=True))
    second_firend_list = list(Firend.objects.filter(user_id__in=firend_ids,
                                                    status=FirendEnum.firend.value)
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
