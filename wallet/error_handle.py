# -*- coding: utf-8 -*-
from django.utils.translation import ugettext

from corelib.errors import BaseError, ErrorCodeField


class WalletError(BaseError):
    TRANSFER_ERROR = ErrorCodeField(20001, ugettext("支付失败"))
    AMOUNT_ERROR = ErrorCodeField(20002, ugettext("余额不足"))
