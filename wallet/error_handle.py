# -*- coding: utf-8 -*-
from django.utils.translation import ugettext

from corelib.errors import BaseError, ErrorCodeField
from .consts import MIN_WITHDRAWALS_AMOUNT, MAX_WITHDRAWALS_AMOUNT


class WalletError(BaseError):
    TRANSFER_ERROR = ErrorCodeField(20001, ugettext("支付失败"))
    AMOUNT_ERROR = ErrorCodeField(20002, ugettext("余额不足"))
    MIN_WITHDRAWAL = ErrorCodeField(20003, ugettext("提现金额不能小于%s元" % MIN_WITHDRAWALS_AMOUNT))
    MIX_WITHDRAWAL = ErrorCodeField(20004, ugettext("提现金额不能大于%s元" % MAX_WITHDRAWALS_AMOUNT))
    DUPLICATE_WITHDRAWAL = ErrorCodeField(20005, ugettext("上次提现尚未完成，请稍后再次操作"))
    WITHDRAWAL_FAIL = ErrorCodeField(20006, ugettext("提现失败"))
    WITHDRAWAL_SUCCESS = ErrorCodeField(20007, ugettext("提现成功, 系统正在进行结算, 您的提现金额将在24小时之内到账"))
