# # -*- coding: utf-8 -*-
# from django.db import models
# from corelib.utils import random_str
#
#
# class Order(models.Model):
#     """
#     bank order用来记录各种交易订单，存钱，取钱，转账等
#     具体业务，如充值，提现，交易，如果需要单独记录，业务系统自己记录
#     """
#     mch_id = models.IntegerField()
#     account_id = models.IntegerField()
#     to_account_id = models.IntegerField(default=0)
#     out_trade_no = models.CharField(max_length=100, unique=True)
#     order_type = models.SmallIntegerField()
#     amount = models.DecimalField(max_digits=11, decimal_places=2)
#     related_amount = models.DecimalField(max_digits=11, decimal_places=2)
#     rate = models.SmallIntegerField()
#     insert_date = models.DateTimeField(auto_now_add=True)
#     end_date = models.DateTimeField(auto_now=True)
#     status = models.SmallIntegerField(default=0)
#
#     def recharge(cls, mch_id, account_id, out_trade_no, amount, rate):
#         pass
#
#     def withdrawal(cls, mch_id, account_id, out_trade_no, amount, rate):
#         pass
#
#     def transfer(cls, mch_id, account_id, to_account_id, out_trade_no, amount, rate):
#         pass
#
#     def add(cls, mch_id, account_id, to_account_id, out_trade_no, order_type, amount):
#         cls.objects.create(mch_id=mch_id,
#                            account_id=account_id,
#                            to_account_id=to_account_id,
#                            out_trade_no=out_trade_no,
#                            order_type=order_type,
#                            amount=amount,
#                            )
#
#
# def create_out_trade_no(num=10):
#     """生成随机的订单号"""
#     return random_str(num=10)
