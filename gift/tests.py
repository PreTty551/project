# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from user.models import User, Friend
from gift.models import Gift, GiftOrder
from wallet.models import Wallet, WalletRecord
from wallet.consts import GIFT_CATGORY


class UsersTestCase(TestCase):
    def setUp(self):
        Gift.add(name="小熊", amount=100, size="m", icon="bear", order="50")
        Gift.add(name="皇冠", amount=500, size="l", icon="bear", order="0")

        self.ida_user = User.objects.add_user(nickname="ida", mobile="1283723123")
        self.mw_user = User.objects.add_user(nickname="mw", mobile="18612345643")

    def setDown(self):
        pass

    def test_gift_list(self):
        response = self.client.get(reverse('gift_list'), {})
        data = json.loads(response.content)

        assert data["data"][1]["name"] == "小熊"

    def test_send_gift_valid(self):
        response = self.client.post(reverse('send_gift'), {"user_id": self.ida_user.id,
                                                           "to_user_id": self.mw_user.id,
                                                           "gift_id": 1,
                                                           "amount": 100})
        # 没钱, 交易失败
        data = json.loads(response.content)
        assert data["error"]["return_code"] == 20002

    def test_send_gift(self):
        wallet = Wallet.get(user_id=1)
        wallet.recharge(amount=10000)
        response = self.client.post(reverse('send_gift'), {"user_id": self.ida_user.id,
                                                           "to_user_id": self.mw_user.id,
                                                           "gift_id": 1,
                                                           "amount": 100})

        order = GiftOrder.objects.all().first()
        assert GiftOrder.objects.count() == 1
        assert order.user_id == 1
        assert order.to_user_id == 2
        assert order.gift_id == 1
        assert order.amount == 100

        wallet = Wallet.get(user_id=1)
        assert wallet.amount == 9900.00

        wallet = Wallet.get(user_id=2)
        assert wallet.amount == 100.00

        assert WalletRecord.objects.count() == 2
        ida_record = WalletRecord.get(owner_id=1)
        assert ida_record.owner_id == 1
        assert ida_record.user_id == 2
        assert ida_record.order_id == str(order.id)
        assert ida_record.amount == 100
        assert ida_record.category == GIFT_CATGORY
        assert ida_record.type == 1
        assert ida_record.desc == "礼物"

        mw_record = WalletRecord.get(owner_id=2)
        assert mw_record.user_id == 1
        assert mw_record.order_id == str(order.id)
        assert mw_record.amount == 100
        assert mw_record.category == GIFT_CATGORY
        assert mw_record.type == 2
        assert mw_record.desc == "礼物"
