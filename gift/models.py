# -*- coding: utf-8 -*-
from django.db import models, transaction

from wallet.models import Wallet, WalletRecord
from wallet.consts import GIFT_CATGORY


class Gift(models.Model):
    name = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    size = models.CharField(max_length=4)
    icon = models.CharField(max_length=50)
    order = models.SmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, gift_id):
        return cls.objects.filter(id=gift_id).first()

    @classmethod
    def add(cls, name, amount, size, icon, order):
        return cls.objects.create(name=name, amount=amount, size=size, icon=icon, order=order)

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount,
            "size": self.size,
            "icon": self.icon,
            "date": self.date
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
def send_gift(owner_id, to_user_id, gift_id, amount, record_msg="礼物"):
    order = GiftOrder.add_order(user_id=owner_id,
                                to_user_id=to_user_id,
                                gift_id=gift_id,
                                amount=amount)

    if order:
        is_success = Wallet.transfer(user_id=owner_id,
                                     to_user_id=to_user_id,
                                     amount=amount)

        if is_success:
            WalletRecord.objects.create(owner_id=owner_id,
                                        user_id=to_user_id,
                                        order_id=order.id,
                                        amount=amount,
                                        category=GIFT_CATGORY,
                                        type=1,
                                        desc=record_msg)

            WalletRecord.objects.create(owner_id=to_user_id,
                                        user_id=owner_id,
                                        order_id=order.id,
                                        amount=amount,
                                        category=GIFT_CATGORY,
                                        type=2,
                                        desc=record_msg)

        #     data = {
        #         "from": order.user_id,
        #         "subtitle": "￥%s" % (order.amount / Decimal(100.0)),
        #         # "title": GIFTS_NOTIFY.get(gift_type) % to_user.nickname,
        #         "to": order.to_user_id,
        #         "type": 1,
        #         "time": int(time.time() * 1000),
        #         "gift_type": gift_type,
        #         "gift_size": GIFTS_SIZE.get(gift_type),
        #         "avatar_url": user.avatar_url
        #     }
        #
        # if int(gift_type) == 1:
        #     data["title"] = GIFTS_NOTIFY.get(gift_type) % (user.nickname, to_user.nickname)
        # else:
        #     data["title"] = GIFTS_NOTIFY.get(gift_type) % to_user.nickname
        # redis.rpush("channel:%s:gitf_queue" % channel_name, json.dumps(data))
        # redis.publish("sub:channel:%s" % channel_name, "1")

            return True
    return False
