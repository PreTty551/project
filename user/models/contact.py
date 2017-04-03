# -*- coding: utf-8 -*-
import random
from django.db import models
from django.conf import settings

from user.models import Ignore, User, Firend


class UserContact(models.Model):
    user_id = models.IntegerField(db_index=True)
    first_name = models.CharField(max_length=20, default="")
    last_name = models.CharField(max_length=20, default="")
    mobile = models.CharField(max_length=20)

    class Meta:
        db_table = "user_contact"

    @classmethod
    def bulk_add(cls, contact_list, user_id):
        contact_list = cls.clean_contact(contact_list=contact_list)
        results = []
        for contact in contact_list:
            _ = cls(user_id=user_id,
                    first_name=contact["first_name"],
                    last_name=contact["last_name"],
                    mobile=contact["mobile"])
            results.append(_)

            # 每500条记录批量插入
            if len(results) >= 500:
                UserContact.objects.bulk_create(results)
                results = []

        if results:
            UserContact.objects.bulk_create(results)

    @classmethod
    def clean_contact(cls, contact_list):
        new_contact_list = []
        for contact in contact_list:
            if not (contact["first_name"] or contact["last_name"]):
                continue

            phones = contact.get("phones", [])
            if not phones:
                continue

            for phone in phones:
                if phone.startswith("400"):
                    continue

                try:
                    mobile = phonenumbers.parse(phone, "CN").national_number
                except:
                    continue

                _ = {
                    "first_name": contact["first_name"],
                    "last_name": contact["last_name"],
                    "mobile": str(mobile)
                }
                new_contact_list.append(_)

        return new_contact_list

    @classmethod
    def get_all_contact(cls, user_id):
        return [contact.contact_dict() for contact in cls.objects.filter(user_id=user_id)]

    # @classmethod
    # def guess_know_user_ids(cls, user_id):
    #     # 我所有的联系人
    #     all_mobile_list = list(cls.objects.filter(user_id=user_id).values_list("mobile", flat=True))
    #     user_mobile_ids = list(User.objects.filter(mobile__in=all_mobile_list).values_list("mobile", flat=True))
    #     all_mobile_list.extend(user_mobile_ids)
    #     filter_mobile_list = set(all_mobile_list)
    #     return list(cls.objects.filter(mobile__in=filter_mobile_list)
    #                            .exclude(user_id=user_id)
    #                            .values_list("user_id", flat=True)
    #                            .distinct())

    def contact_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mobile": self.mobile,
            "avatar_url": "%scontact_avatar_%s@3x-min.png" % (settings.MEDIA_URL, random.randint(1, 9))
        }

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "mobile": self.mobile
        }


def get_contact_in_say(owner_id):
    ignore_user_ids = Ignore.get_contacts_in_say(owner_id=owner_id)
    all_mobile_list = list(UserContact.objects.filter(user_id=owner_id).values_list("mobile", flat=True))
    user_ids = list(User.objects.filter(mobile__in=all_mobile_list)
                                .exclude(id__in=ignore_user_ids)
                                .values_list("id", flat=True))

    ignore_user_ids = Ignore.get_invite_firends(owner_id=owner_id)
    result = []
    for user_id in user_ids:
        user = User.get(id=user_id)
        basic_info = user.basic_info()
        is_invited_user = Firend.is_invited_user(user_id=owner_id, firend_id=user_id)
        basic_info["is_invited_user"] = is_invited_user
        result.append(basic_info)
    return result


def get_contact_out_say(owner_id):
    ignore_user_ids = Ignore.get_contacts_out_say(owner_id=owner_id)
    all_mobile_list = list(UserContact.objects.filter(user_id=owner_id).values_list("mobile", flat=True))
    mobile_ids = list(User.objects.filter(mobile__in=all_mobile_list)
                                  .exclude(id__in=ignore_user_ids)
                                  .values_list("mobile", flat=True))

    out_say_mobiles = set(mobile_ids) ^ set(all_mobile_list)
    result = []
    for mobile in out_say_mobiles:
        user = User.objects.filter(mobile=mobile).first()
        basic_info = user.basic_info()
        result.append(basic_info)
    return result
