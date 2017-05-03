# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F

from decimal import Decimal

from wallet.consts import MIN_TRANSFER_AMOUNT, MAX_TRANSFER_AMOUNT
from wallet.consts import MIN_WITHDRAWALS_AMOUNT, MAX_WITHDRAWALS_AMOUNT
from wallet.consts import WITHDRAWAL_APPLY, WITHDRAWAL_SUCCESS, WITHDRAWAL_FAIL
from wallet.consts import RECHARGE_CATEGORY
from wallet.error_handle import WalletError


class Wallet(models.Model):
    user_id = models.IntegerField(unique=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, user_id):
        wallet = cls.objects.filter(user_id=user_id).first()
        if not wallet:
            wallet = cls.objects.create(user_id=user_id)
        return wallet

    def validate(self, amount):
        if self.amount - Decimal(amount) < 0:
            return WalletError.AMOUNT_ERROR

    def transfer_validate(self, amount, wechat=False):
        amount = Decimal(amount)
        if amount < Decimal(str(MIN_TRANSFER_AMOUNT)):
            return "自定义金额不能小于%s元" % MIN_TRANSFER_AMOUNT
        elif amount > Decimal(str(MAX_TRANSFER_AMOUNT)):
            return "自定义金额不能大于%s元" % MAX_TRANSFER_AMOUNT

        if not wechat:
            if self.amount - amount * 100 < 0:
                return u"账户余额不足"

    def withdrawals_validate(self, amount):
        amount = Decimal(amount)
        if amount < Decimal(str(MIN_WITHDRAWALS_AMOUNT)):
            return WalletError.MIN_WITHDRAWAL
        elif amount > Decimal(str(MAX_WITHDRAWALS_AMOUNT)):
            return WalletError.MAX_WITHDRAWAL
        elif self.amount - amount * 100 < 0:
            return WalletError.AMOUNT_ERROR

        withdrawal = Withdrawals.objects.filter(user_id=self.user_id, status=WITHDRAWAL_APPLY).first()
        if withdrawal:
            return WalletError.DUPLICATE_WITHDRAWAL

    def plus(self, amount):
        self.amount = F("amount") + Decimal(amount)
        self.save()
        return self

    def minus(self, amount):
        self.amount = F("amount") - Decimal(amount)
        self.save()
        return self

    @classmethod
    @transaction.atomic()
    def transfer(cls, user_id, to_user_id, amount):
        user = cls.get(user_id=user_id)
        user.minus(amount=amount)

        to_user = cls.get(user_id=to_user_id)
        amount = Decimal(amount) * Decimal("0.7")
        to_user.plus(amount=amount)
        return True

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "amount": yuan(self.amount)
        }


class WalletRecord(models.Model):
    owner_id = models.IntegerField(default=0)
    user_id = models.IntegerField()
    out_trade_no = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    category = models.SmallIntegerField(default=0)
    type = models.SmallIntegerField()
    desc = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get(cls, owner_id):
        return cls.objects.filter(owner_id=owner_id).first()


class WalletRecharge(models.Model):
    """ 充值 """
    user_id = models.IntegerField()
    out_trade_no = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "wallet_recharge"

    @property
    def is_pay_success(self):
        return self.status == 1

    @classmethod
    @transaction.atomic()
    def recharge_callback(cls, out_trade_no):
        wr = cls.objects.filter(out_trade_no=out_trade_no).first()
        if wr and not wr.is_pay_success:
            wallet = Wallet.get(user_id=wr.user_id)
            is_success = wallet.plus(amount=wr.amount)
            if is_success:
                wr.status = 1
                wr.save()

                WalletRecord.objects.create(owner_id=wr.user_id,
                                            user_id=wr.user_id,
                                            out_trade_no=out_trade_no,
                                            amount=wr.amount,
                                            category=RECHARGE_CATEGORY,
                                            type=1,
                                            desc="充值")
                return True


class Withdrawals(models.Model):
    """ 提现 """
    openid = models.CharField(max_length=200)
    user_id = models.IntegerField()
    status = models.SmallIntegerField(default=0)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    wechat_recode = models.CharField(max_length=50, default="")

    class Meta:
        db_table = "wallet_withdrawal"

    @classmethod
    @transaction.atomic()
    def apply(cls, openid, user_id, amount):
        cls.objects.create(openid=openid,
                           user_id=user_id,
                           amount=amount)
        wallet = Wallet.get(user_id=user_id)
        wallet.minus(amount=amount)
        return True

    @classmethod
    def enterprise_pay(cls, openid, amount):
        recode = wechat_pay.transfer.transfer(user_id=obj.openid,
                                              amount=wechat_amount,
                                              desc="账户提现",
                                              check_name="NO_CHECK")

        if recode["return_code"] == "SUCCESS" and recode["result_code"] == "SUCCESS":
            return True, recode
        else:
            return False, recode

    @classmethod
    def withdrawal(cls):
        withdrawal_recodes = cls.objects.filter(status=WITHDRAWAL_APPLY)
        for wr in withdrawal_recodes:
            is_success, recode = cls.enterprise_pay(openid=wr.openid, amount=wr.amount)
            if is_success:
                Withdrawals.objects.filter(user_id=obj.user_id).update(status=WITHDRAWAL_SUCCESS)
                wallet = Wallet.get(user_id=wr.user_id)
                wallet.minus(amount=wr.amount)
            else:
                Withdrawals.objects.filter(user_id=obj.user_id).update(wechat_recode=recode["err_code"],
                                                                       status=WITHDRAWAL_FAIL)


def get_related_amount(amount):
    """ 得到格式化并减去手续费后的金额 """
    amount = str(Decimal(str(amount)) * 100)
    if amount.find(".") != -1:
        amount = amount.rstrip("0").rstrip(".")
    return Decimal(amount)


def yuan(amount):
    """金额(元)"""
    return (Decimal(amount) / Decimal("100")).quantize(Decimal('0.00'))


def is_disable_wallet(user):
    if user.id == 45:
        return True
    return False
