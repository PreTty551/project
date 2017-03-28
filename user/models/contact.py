# -*- coding: utf-8 -*-
from django.db import models


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

    @classmethod
    def guess_know_user_ids(cls, user_id):
        all_mobile_list = list(cls.objects.filter(user_id=user_id).values_list("mobile", flat=True))
        user_mobile_ids = list(User.objects.filter(mobile__in=all_mobile_list).values_list("mobile", flat=True))
        all_mobile_list.extend(user_mobile_ids)
        filter_mobile_list = set(all_mobile_list)
        return list(cls.objects.filter(mobile__in=filter_mobile_list)
                               .exclude(user_id=user_id)
                               .values_list("user_id", flat=True)
                               .distinct())

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
