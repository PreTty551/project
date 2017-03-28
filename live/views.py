# -*- coding: utf-8 -*-
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from corelib.decorators import login_required_404
from corelib.utils import JsonResponseSuccess
from corelib.agora import Agora

from livemedia.models import Channel, ChannelMember, GuessWord
from user.models import User, FollowUser
from log.models import ActiveUser


@login_required_404
def livemedia_list(request):
    channels = [channel.to_dict() for channel in Channel.objects.filter(member_count__gt=0)]
    firends = Firend.get_firends(owner_id=request.user.id)
    online_firends = []
    offline_firends = []
    for firend in firends:
        user = User.get(id=firend.user_id)
        if user:
            basic_info = user.basic_info()
            if user.is_online():
                basic_info["is_online"] = True
                online_firends.append(basic_info)
            else:
                basic_info["is_online"] = False
                basic_info["natural_time"] = user.natural_time
                offline_firends.append(basic_info)

    return JsonResponseSuccess({"channels": channels,
                                "online_firends": online_firends,
                                "offline_firends": offline_firends})


@login_required_404
def create_channel(request):
    channel = Channel.create_channel(user_id=request.user.id)
    if channel:
        agora = Agora(user_id=request.user.id)
        channel_key = agora.get_channel_madia_key(channel_name=channel.channel_id.encode("utf8"))

        user = ActiveUser.objects.filter(user_id=request.user.id).first()
        if user:
            user.date = timezone.now()
            user.save()

        return JsonResponseSuccess({"channel_id": channel.channel_id, "channel_key": channel_key})


@require_http_methods(["POST"])
@login_required_404
def join_channel(request):
    channel_id = request.POST.get("channel_id")
    in_channel_uids = request.POST.get("in_channel_uids", [])

    if not channel_id:
        return HttpResponseBadRequest()

    if in_channel_uids:
        in_channel_uids = [channel_uid for channel_uid in in_channel_uids.split(" ")]

    agora = Agora(user_id=request.user.id)
    channel_key = agora.get_channel_madia_key(channel_name=channel_id.encode("utf8"))

    channel = Channel.get_channel(channel_id=channel_id)
    if not channel:
        return HttpResponseBadRequest()

    if channel.is_lock:
        return JsonResponseSuccess({"is_lock": True})

    Channel.join_channel(channel_id=channel_id,
                         user_id=request.user.id,
                         in_channel_uids=in_channel_uids)
    return JsonResponseSuccess({"channel_id": channel_id, "channel_key": channel_key})


@require_http_methods(["POST"])
@login_required_404
def quit_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.quit_channel(user_id=request.user.id)
    return JsonResponseSuccess()


@require_http_methods(["POST"])
@login_required_404
def delete_channel(request):
    channel_id = request.POST.get("channel_id")
    Channel.delete_channel(channel_id=channel_id)
    return JsonResponseSuccess()


@login_required_404
def signaling_key(request):
    agora = Agora(user_id=request.user.id)
    signaling_key = agora.get_signaling_key()
    return JsonResponseSuccess({"signaling_key": signaling_key})


@require_http_methods(["POST"])
def user_online_callback(request):
    user_id = request.POST.get("account")
    is_online = request.POST.get("is_online", True)

    if not bool(is_online):
        ChannelMember.clear_channel(user_id=user_id)

    return JsonResponseSuccess()


@require_http_methods(["POST"])
@login_required_404
def lock_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.lock()
        return JsonResponseSuccess()
    return HttpResponseBadRequest()


@require_http_methods(["POST"])
@login_required_404
def unlock_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.unlock()
        return JsonResponseSuccess()
    return HttpResponseBadRequest()


@require_http_methods(["POST"])
@login_required_404
def guess_word(request):
    channel_id = request.POST.get("channel_id")

    data = {
        "type": 3,
        "user_id": request.user.id,
        "content": GuessWord.get_random_word()
    }

    agora = Agora(user_id=request.user.id)
    agora.send_cannel_msg(channel_id=channel_id, **data)
    return JsonResponseSuccess()


@require_http_methods(["POST"])
@login_required_404
def close_guess_word(request):
    channel_id = request.POST.get("channel_id")
    data = {
        "type": 4,
        "user_id": request.user.id,
    }

    agora = Agora(user_id=request.user.id)
    agora.send_cannel_msg(channel_id=channel_id, **data)
    return JsonResponseSuccess()
