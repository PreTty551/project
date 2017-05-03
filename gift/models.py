# -*- coding: utf-8 -*-
import time
import json

from django.db import models, transaction
from decimal import Decimal

from corelib.redis import redis
from corelib.agora import Agora

from wallet.models import Wallet, WalletRecord
from wallet.consts import GIFT_CATEGORY
from user.models import User


class Gift(models.Model):
    name = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    size = models.CharField(max_length=4)
    icon = models.CharField(max_length=50)
    order = models.SmallIntegerField()
    message = models.CharField(max_length=50, default="")
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, gift_id):
        return cls.objects.filter(id=gift_id).first()

    @classmethod
    def add(cls, name, amount, size, icon, order):
        return cls.objects.create(name=name, amount=amount, size=size, icon=icon, order=order)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount / 100,
            "size": self.size,
            "icon": self.id,
        }

    class Meta:
        db_table = "gift"


class GiftOrder(models.Model):
    user_id = models.IntegerField()
    to_user_id = models.IntegerField()
    gift_id = models.SmallIntegerField()
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    status = models.SmallIntegerField(default=0)
    add_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gift_order"

    @classmethod
    def add_order(cls, user_id, to_user_id, gift_id, amount):
        return cls.objects.create(user_id=user_id,
                                  to_user_id=to_user_id,
                                  gift_id=gift_id,
                                  amount=amount)

    def update_order(cls, order_id, status):
        cls.objects.filter(id=order_id).update(status=status)


@transaction.atomic()
def send_gift(owner_id, to_user_id, gift_id, amount, channel_id, record_msg="礼物"):
    order = GiftOrder.add_order(user_id=owner_id,
                                to_user_id=int(to_user_id),
                                gift_id=gift_id,
                                amount=amount)

    if order:
        is_success = Wallet.transfer(user_id=owner_id,
                                     to_user_id=to_user_id,
                                     amount=amount)

        if is_success:
            WalletRecord.objects.create(owner_id=owner_id,
                                        user_id=to_user_id,
                                        out_trade_no=order.id,
                                        amount=amount,
                                        category=GIFT_CATEGORY,
                                        type=1,
                                        desc=record_msg)

            WalletRecord.objects.create(owner_id=to_user_id,
                                        user_id=owner_id,
                                        out_trade_no=order.id,
                                        amount=amount,
                                        category=GIFT_CATEGORY,
                                        type=2,
                                        desc=record_msg)

            gift = Gift.get(gift_id)
            user = User.get(owner_id)
            to_user = User.get(to_user_id)
            _ = {
                "type": 1,
                "data": {
                    "from": order.user_id,
                    "subtitle": "￥%s" % (order.amount / Decimal(100.0)),
                    "title": gift.message % to_user.nickname,
                    "to": order.to_user_id,
                    "time": int(time.time() * 1000),
                    "gift_size": gift.size,
                    "avatar_url": user.avatar_url,
                    "icon": int(gift_id)
                }
            }

            agora = Agora(user_id=owner_id)
            agora.send_cannel_msg(channel_id=channel_id, **_)
            return True
    return False


def test_gift_queue(owner_id, to_user_id, channel_id, gift_id=1):
    gift = Gift.get(gift_id)
    user = User.get(owner_id)
    to_user = User.get(to_user_id)
    data = {
        "from": owner_id,
        "subtitle": "￥%s" % (gift.amount / Decimal(100.0)),
        "title": gift.message % to_user.nickname,
        "to": to_user.to_user_id,
        "type": 1,
        "time": int(time.time() * 1000),
        "gift_size": gift.size,
        "avatar_url": user.avatar_url,
        "icon": 1
    }

    agora = Agora(user_id=data["from"])
    agora.send_cannel_msg(channel_id=channel_id, **data)
    time.sleep(2)
