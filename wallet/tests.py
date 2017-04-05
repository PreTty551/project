from django.test import TestCase, TransactionTestCase

from corelib.utils import random_str

from wallet.models import WalletRecharge, Wallet, WalletRecord
from user.models import User


class AccountTestCase(TransactionTestCase):

    def setUp(self):
        self.ida = User.objects.add_user(nickname="ida", mobile="18511223342")

    def test_recharge(self):
        wallet = Wallet.get(self.ida.id)
        wallet.amount == 0.00
        wr = WalletRecharge.objects.create(user_id=self.ida.id,
                                           out_trade_no=random_str(),
                                           amount="5000")

        out_trade_no = wr.out_trade_no
        assert wr.status == 0

        WalletRecharge.recharge_callback(wr.out_trade_no)
        wr = WalletRecharge.objects.filter(out_trade_no=out_trade_no).first()
        assert wr.status == 1

        wallet = Wallet.get(self.ida.id)
        assert wallet.amount == 5000.00

        record = WalletRecord.objects.filter(out_trade_no=out_trade_no).first()
        assert record is not None
