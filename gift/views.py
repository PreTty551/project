# -*- coding: utf-8 -*-
from django.shortcuts import render

from corelib.http import JsonResponse
from corelib.decorators import login_required_404

from gift.models import Gift, send_gift
from gift.error_handle import GiftError
from wallet.models import Wallet


@login_required_404
def gift_list(request):
    gifts = Gift.objects.all().order_by("order")
    result = [gift.to_dict() for gift in gifts]
    return JsonResponse(result)


@login_required_404
def gift_transfer(request):
    to_user_id = request.POST.get("to_user_id")
    gift_id = request.POST.get("gift_id")
    channel_id = request.POST.get("channel_id")

    if request.user.id in [170954, 156846, 170968, 170970, 170974]:
        return JsonResponse(error=GiftError.TRANSFER_GIFT_ERROR)

    if int(to_user_id) in [170954, 156846, 170968, 170970, 170974]:
        return JsonResponse(error=GiftError.TRANSFER_GIFT_ERROR)

    amount = Gift.get(gift_id).amount
    wallet = Wallet.get(user_id=request.user.id)
    valid = wallet.validate(amount=amount)
    if valid is not None:
        return JsonResponse(error=valid)

    is_success = send_gift(owner_id=request.user.id,
                           to_user_id=to_user_id,
                           gift_id=gift_id,
                           amount=amount,
                           channel_id=channel_id)
    if is_success:
        return JsonResponse()
    return JsonResponse(error=GiftError.TRANSFER_GIFT_ERROR)
