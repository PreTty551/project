# -*- coding: utf-8 -*-

from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from corelib.decorators import login_required_404
from corelib.agora import Agora
from corelib.http import JsonResponse
from corelib.websocket import Websocket

from live.models import Channel, ChannelMember, GuessWord, InviteChannel
from live.consts import ChannelType
from user.models import User, Friend, UserContact, two_degree_relation, Place


TEST_USER_IDS = []


@login_required_404
def livemedia_list(request):
    if request.user.id in TEST_USER_IDS:
        res = request.get("https://gouhuoapp.com/api/v2/livemedia/list/")
        res = res.json()
        channels = res["channels"]

    # channels = [channel.to_dict() for channel in Channel.objects.filter(member_count__gt=0)]
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    friend_list = []
    for friend_id in friend_ids:
        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            friend_list.append(basic_info)

    two_degree_friends = two_degree_relation(user_id=request.user.id)
    return JsonResponse({"channels": channels,
                         "friends": friend_list,
                         "contacts_in_say": UserContact.get_contacts_in_app(owner_id=request.user.id),
                         "contacts_out_say": UserContact.get_contacts_out_app(owner_id=request.user.id),
                         "two_degree_friends": two_degree_friends})


def near_channel_list(request):
    """
    这里有两种实现方式, 后续可以根据需求或数据量调整
    1. 先查找所有附近类型的房间，再查这些房间用户，算附近排序(现在使用中)
    2. 先直接查找附近n距离内的用户，再根据这些用户找到房间
    """
    channel_ids = Channel.objects.filter(channel_type=ChannelType.near.value).values_list("id", flat=True)
    user_ids = ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True)
    place = Place.get(user_id=request.user.id)
    if not place:
        return JsonResponse({"channels": []})

    user_locations = Place.get_multi_user_dis(user_ids=user_ids)
    sorted_user_ids = sorted(user_locations.items(), key=lambda item: item[1])

    channels = []
    for user_id in sorted_user_ids:
        channel_id = ChannelMember.objects.filter(channel_type=1, user_id=user_id).values_list("channel_id", flat=True)
        channel = Channel.get_channel(channel_id=channel_id)
        if not channel:
            continue

        channels.append(channel.to_dict())
    return JsonResponse({"channels": channels})


def private_channel_list(request):
    channel_ids = InviteChannel.objects.filter(to_user_id=request.user.id).values_list("channel_id", flat=True)
    channels = [Channel.get_channel(channel_id=channel_id).to_dict() for channel_id in channel_ids]
    return JsonResponse({"channels": channels})


@login_required_404
def create_channel(request):
    channel_type = int(request.POST.get("channel_type", ChannelType.normal.value))

    try:
        ChannelType(channel_type)
    except ValueError:
        return HttpResponseBadRequest()

    if request.user.id in TEST_USER_IDS:
        res = requests.post("https://gouhuoapp.com/api/v2/livemedia/channel/create/")
        res = res.json()
        return JsonResponse({"channel_id": res["channel_id"],
                             "channel_key": res["hannel_key"]})

    Channel.create_channel(user_id=request.user.id, channel_type=channel_type)
    if channel:
        agora = Agora(user_id=request.user.id)
        channel_key = agora.get_channel_madia_key(channel_name=channel.channel_id)

        user = User.get(id=request.user.id)
        if user:
            user.last_login = timezone.now()
            user.save()

        return JsonResponse({"channel_id": channel.channel_id, "channel_key": channel_key})


@login_required_404
def invite_channel(request):
    invite_user_id = request.POST.get("invite_user_id")
    channel = Channel.invite_channel(user_id=request.user.id, invite_user_id=invite_user_id)
    if channel:
        agora = Agora(user_id=request.user.id)
        channel_key = agora.get_channel_madia_key(channel_name=channel.channel_id)

        user = User.get(id=request.user.id)
        if user:
            user.last_login = timezone.now()
            user.save()

        return JsonResponse({"channel_id": channel.channel_id, "channel_key": channel_key})


@require_http_methods(["POST"])
@login_required_404
def join_channel(request):
    channel_id = request.POST.get("channel_id")

    if not channel_id:
        return HttpResponseBadRequest()

    if request.user.id in TEST_USER_IDS:
        res = request.get("https://gouhuoapp.com/api/v2/livemedia/channel/join/", data={"channel_id": channel_id})

        agora = Agora(user_id=request.user.id)
        channel_key = agora.get_channel_madia_key(channel_name=channel_id.encode("utf8"))
        return JsonResponse({"channel_id": channel_id, "channel_key": channel_key})

    agora = Agora(user_id=request.user.id)
    channel_key = agora.get_channel_madia_key(channel_name=channel_id.encode("utf8"))

    channel = Channel.get_channel(channel_id=channel_id)
    if not channel:
        return HttpResponseBadRequest()

    if channel.is_lock:
        return JsonResponse({"is_lock": True})

    Channel.join_channel(channel_id=channel_id,
                         user_id=request.user.id,
                         in_channel_uids=in_channel_uids)
    return JsonResponse({"channel_id": channel_id, "channel_key": channel_key})


@require_http_methods(["POST"])
@login_required_404
def quit_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.quit_channel(user_id=request.user.id)
    return JsonResponse()


@require_http_methods(["POST"])
@login_required_404
def delete_channel(request):
    channel_id = request.POST.get("channel_id")
    Channel.delete_channel(channel_id=channel_id)
    return JsonResponse()


@login_required_404
def signaling_key(request):
    agora = Agora(user_id=request.user.id)
    signaling_key = agora.get_signaling_key()
    return JsonResponse({"signaling_key": signaling_key})


@require_http_methods(["POST"])
def user_online_callback(request):
    user_id = request.POST.get("account")
    is_online = request.POST.get("is_online", True)

    if not bool(is_online):
        ChannelMember.clear_channel(user_id=user_id)

    return JsonResponse()


@require_http_methods(["POST"])
@login_required_404
def lock_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.lock()
        return JsonResponse()
    return HttpResponseBadRequest()


@require_http_methods(["POST"])
@login_required_404
def unlock_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.unlock()
        return JsonResponse()
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
    return JsonResponse()


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
    return JsonResponse()


def push_to_user(request):
    receiver_id = request.POST.get("receiver_id")

    max_number = 20
    push_number = mc.get("push_number:u:%s:r:%s" % (request.user.id, receiver_id)) or 0
    if push_number > max_number:
        return JsonResponseSuccess()

    icon = ""
    message = u"👉 %s邀请你来开Party" % request.user.nickname
    for i in range(push_number):
        icon += u"👉"

    message = u"%s%s" % (icon, message)
    websocket = Websocket(receiver_id=receiver_id)
    websocket.push(message=message)

    member = ChannelMember.objects.filter(user_id=request.user.id).first()
    if member:
        push_number += 1
        LeanCloudIOS.async_push(receive_id=receiver_id, message=message, msg_type=8, channel_id=member.channel_id)
        mc.set("push_number:u:%s:r:%s" % (request.user.id, receiver_id), push_number, 60)

    return JsonResponseSuccess()
