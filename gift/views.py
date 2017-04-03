# -*- coding: utf-8 -*-
from django.shortcuts import render

from corelib.http import JsonResponse
from gift.models import Gift, send_gift
from wallet.models import Wallet


def gift_list(request):
    gifts = Gift.objects.all().order_by("order")
    result = [gift.to_dict() for gift in gifts]
    return JsonResponse(result)


def gift_transfer(request):
    user_id = request.POST.get("user_id")
    to_user_id = request.POST.get("to_user_id")
    gift_id = request.POST.get("gift_id")
    order_id = request.POST.get("order_id")
    amount = request.POST.get("amount")

    wallet = Wallet.get(user_id=user_id)
    valid = wallet.validate(amount=amount)
    if valid is not None:
        return JsonResponse(error=valid)

    is_success = send_gift(owner_id=user_id,
                           to_user_id=to_user_id,
                           gift_id=gift_id,
                           amount=amount)
    if is_success:
        return JsonResponse()
    return JsonResponse("交易失败")
