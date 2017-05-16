# -*- coding: utf-8 -*-
import json
import random
import phonenumbers

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext

from corelib.errors import BaseError, ErrorCodeField
from corelib.mc import cache

from .user import User
from .ignore import Ignore
from .friend import Friend, InviteFriend
from user.consts import UserEnum, MC_RECOMMEND_CONTACT


class UserContact(models.Model):
    user_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20, db_index=True)

    class Meta:
        db_table = "user_contact"

    @classmethod
    def bulk_add(cls, contact_list, user_id):
        contact_list = cls.clean_contact(contact_list=contact_list)
        results = []
        for contact in contact_list:
            name = contact["name"]
            _ = cls(user_id=user_id,
                    name=name[:20],
                    mobile=contact["mobile"])
            results.append(_)

            # 每500条记录批量插入
            if len(results) >= 500:
                UserContact.objects.bulk_create(results)
                results = []

        if results:
            UserContact.objects.bulk_create(results)
            return True

    @classmethod
    def clean_contact(cls, contact_list):
        new_contact_list = []
        for contact in contact_list:
            if not contact.get("name"):
                continue

            phones = contact.get("phones", [])
            if not phones:
                continue

            for phone in phones:
                try:
                    mobile = phonenumbers.parse(phone, "CN").national_number
                except:
                    continue

                if str(mobile).startswith("400"):
                    continue

                if contact["name"] in ["钉钉", "滴滴出行", "钉钉官方短信", "钉钉DING消息"]:
                    continue

                _ = {
                    "name": contact["name"],
                    "mobile": str(mobile)
                }
                new_contact_list.append(_)

        return new_contact_list

    @classmethod
    def get_all_contact(cls, user_id):
        return [contact.to_dict() for contact in cls.objects.filter(user_id=user_id)]

    @classmethod
    def get_contacts_in_app(cls, owner_id):
        ignore_user_ids = Ignore.get_contacts_in_app(owner_id=owner_id)
        friend_ids = Friend.get_friend_ids(user_id=owner_id)
        all_mobile_list = list(UserContact.objects.filter(user_id=owner_id).values_list("mobile", flat=True))
        invite_friends = list(InviteFriend.objects.filter(invited_id=owner_id).values_list("user_id", flat=True))
        user_ids = list(User.objects.filter(mobile__in=all_mobile_list)
                                    .exclude(id__in=ignore_user_ids)
                                    .exclude(id__in=friend_ids)
                                    .exclude(id__in=invite_friends)
                                    .values_list("id", flat=True))

        results = []
        for user_id in user_ids:
            user = User.get(id=user_id)
            if not user:
                continue
            basic_info = user.basic_info()
            results.append(basic_info)

        return results

    @classmethod
    def get_contacts_out_app(cls, owner_id):
        ignore_user_ids = list(Ignore.objects.filter(ignore_type=2).values_list("ignore_id", flat=True))
        all_mobile_list = list(UserContact.objects.filter(user_id=owner_id).values_list("mobile", flat=True))
        mobile_ids = list(User.objects.filter(mobile__in=all_mobile_list)
                                      .exclude(id__in=ignore_user_ids)
                                      .values_list("mobile", flat=True))

        out_say_mobiles = set(mobile_ids) ^ set(all_mobile_list)
        result = []
        for mobile in out_say_mobiles:
            uc = UserContact.objects.filter(user_id=owner_id, mobile=mobile).first()
            if uc:
                result.append(uc.to_dict())
        return result

    @classmethod
    @cache(MC_RECOMMEND_CONTACT % '{owner_id}', 3600 * 24)
    def recommend_contacts(cls, owner_id, limit=None):
        ignore_ids = list(Ignore.objects.filter(owner_id=owner_id, ignore_type=2).values_list("ignore_id", flat=True))
        all_mobile_list = list(UserContact.objects.filter(user_id=owner_id)
                                                  .exclude(id__in=ignore_ids).values_list("mobile", flat=True))
        mobile_ids = User.objects.filter(mobile__in=all_mobile_list).values_list("mobile", flat=True)
        mobile_ids = set(mobile_ids) ^ set(all_mobile_list)

        my_contact_dict = {}
        my_contact_list = UserContact.objects.filter(user_id=owner_id)
        for contact in my_contact_list:
            my_contact_dict[contact.mobile] = (contact.name, contact.id)

        common_contacts = UserContact.objects.filter(mobile__in=mobile_ids).exclude(user_id=owner_id)
        contacts = {}
        contacts_map = {}
        user_ids = []
        for contact in common_contacts:
            _ = contacts.setdefault(contact.mobile, [])
            _.append(contact.user_id)
            contacts_map[contact.mobile] = my_contact_dict[contact.mobile]
            user_ids.append(contact.user_id)

        results = []
        for mobile, user_ids in contacts.items():
            rate = 0
            # for user_id in user_ids:
            #     friend_ids = Friend.get_friend_ids(user_id=user_id)
            #     friend_count = len(set(user_ids) & set(friend_ids))
            #     rate += friend_count
            results.append((mobile, rate))

        sorted_results = sorted(results, key=lambda item: item[1])
        if limit is not None:
            sorted_results = sorted_results[:limit]

        return [{"name": contacts_map[r[0]][0], "mobile": r[0], "id": contacts_map[r[0]][1]} for r in sorted_results]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "user_id": self.user_id,
        }


class ContactError(BaseError):
    IMPORT_ERROR = ErrorCodeField(30001, ugettext("导入通讯录失败"))
