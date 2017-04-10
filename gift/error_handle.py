# -*- coding: utf-8 -*-
from django.utils.translation import ugettext

from corelib.errors import BaseError, ErrorCodeField


class GiftError(BaseError):
    TRANSFER_GIFT_ERROR = ErrorCodeField(30001, ugettext("送礼物失败"))
