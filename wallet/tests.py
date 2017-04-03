from django.test import TestCase, TransactionTestCase


class AccountTestCase(TransactionTestCase):

    def setUp(self):
        pass

    def test_bank(self):
        account = Back.get_account(account_id=3)
        account.plus(100)
        account.save_money(100)
