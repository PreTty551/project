# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models, transaction
from django.db.models import F

from decimal import Decimal

from wallet.consts import MIN_TRANSFER_AMOUNT, MAX_TRANSFER_AMOUNT
from wallet.consts import MIN_WITHDRAWALS_AMOUNT, MAX_WITHDRAWALS_AMOUNT
from wallet.consts import WITHDRAWAL_APPLY, WITHDRAWAL_SUCCESS, WITHDRAWAL_FAIL
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
            return u"提现金额不能小于%s元" % MIN_WITHDRAWALS_AMOUNT
        elif amount > Decimal(str(MAX_WITHDRAWALS_AMOUNT)):
            return u"提现金额不能大于%s元" % MAX_WITHDRAWALS_AMOUNT
        elif self.amount - amount * 100 < 0:
            return u"账户余额不足"

        withdrawal = Withdrawals.objects.filter(user_id=self.user_id, status=WITHDRAWAL_APPLY).first()
        if withdrawal:
            return u"上次提现尚未完成，请稍后再次操作"

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
        to_user.plus(amount=amount)
        return True

    @transaction.atomic()
    def recharge(self, amount):
        return self.plus(amount=amount)


class WalletRecord(models.Model):
    owner_id = models.IntegerField(default=0)
    user_id = models.IntegerField()
    order_id = models.CharField(max_length=50)
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
    def recharge_callback(cls, out_trade_no):
        wr = cls.objects.filter(out_trade_no=out_trade_no)
        if wr and not wr.is_pay_success:
            wallet = Wallet.get(user_id=wr.user_id)
            is_success = wallet.recharge(amount=wr.amount)
            if is_success:
                wr.status = ORDER_SUCCESS
                wr.save()
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
    def apply(cls, openid, user_id, amount):
        return cls.objects.create(openid=openid,
                                  user_id=user_id,
                                  amount=amount)

    def withdrawal(cls):
        withdrawal_recodes = cls.objects.filter(status=0)
        for wr in withdrawal_recodes:
            wallet = Wallet.get(user_id=wr.user_id)
            is_success, res = wallet.enterprise_pay(openid=wr.openid, amount=wr.amount, desc="提现")
            if is_success:
                wr.status = 1
                wr.save()
            else:
                wr.status = 2
                wr.wechat_recode = res["err_code"]
                wr.save()
