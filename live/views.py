# -*- coding: utf-8 -*-
import time
import random
import requests

from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from corelib.decorators import login_required_404
from corelib.agora import Agora
from corelib.http import JsonResponse
from corelib.websocket import Websocket

from live.models import Channel, ChannelMember, GuessWord, InviteChannel, InviteParty
from live.consts import ChannelType
from user.models import User, Friend, UserContact, Place, guess_know_user
from user.consts import UserEnum

TEST_USER_IDS = []


def refresh_list(request):
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    channel_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("channel_id", flat=True).distinct()
    for channel_id in channel_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        if channel.channel_type == ChannelType.private.value:
            continue
        channels.append(channel.to_dict())

    invite_party_ids = InviteParty.get_invites(user_id=request.user.id)

    friend_list = []
    for user_id in invite_party_ids:
        user = User.get(id=user_id)
        if user:
            basic_info = user.basic_info()
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["is_hint"] = True
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels,
                         "friends": friend_list})


def refresh_home_list(request):
    channels = []
    invite_party_ids = InviteParty.objects.filter(
                            to_user_id=request.user.id,
                            party_type=ChannelType.private.value).values_list("channel_id", flat=True)
    for party_id in invite_party_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        channels.append(channel.to_dict())

    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    channel_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("channel_id", flat=True).distinct()
    for channel_id in channel_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        if channel.channel_type == ChannelType.private.value:
            continue
        channels.append(channel.to_dict())

    invite_party_ids = InviteParty.get_invites(user_id=request.user.id)

    friend_list = []
    for user_id in invite_party_ids:
        user = User.get(id=user_id)
        if user:
            basic_info = user.basic_info()
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["is_hint"] = True
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels,
                         "friends": friend_list})


@login_required_404
def home_list(request):
    """
    首页房间列表，包含
       1. 邀请我的private party
       2. 我的好友开的public party
       3. 好友可见的party
    """
    channels = []
    invite_party_ids = InviteParty.objects.filter(
                            to_user_id=request.user.id,
                            party_type=ChannelType.private.value).values_list("channel_id", flat=True)
    for party_id in invite_party_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        channels.append(channel.to_dict())

    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    channel_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("channel_id", flat=True).distinct()
    for channel_id in channel_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        if channel.channel_type == ChannelType.private.value:
            continue
        channels.append(channel.to_dict())

    invite_party_ids = InviteParty.get_invites(user_id=request.user.id)

    friend_list = []
    for user_id in invite_party_ids:
        user = User.get(id=user_id)
        if user:
            basic_info = user.basic_info()
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["is_hint"] = True
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels,
                         "friends": friend_list,
                         "guess_know_users": guess_know_user(request.user.id),
                         "guess_contacts": UserContact.recommend_contacts(request.user.id, 20)})


@login_required_404
def livemedia_list(request):
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    channel_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("channel_id", flat=True).distinct()
    channels = []
    for channel_id in channel_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        if channel.channel_type in [ChannelType.private.value, ChannelType.public.value]:
            continue
        channels.append(channel.to_dict())

    invite_party_ids = InviteParty.get_invites(user_id=request.user.id)

    friend_list = []
    for user_id in invite_party_ids:
        user = User.get(id=user_id)
        if user:
            basic_info = user.basic_info()
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["is_hint"] = True
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels,
                         "friends": friend_list,
                         "guess_know_users": guess_know_user(request.user.id),
                         "guess_contacts": UserContact.recommend_contacts(request.user.id, 20)})


def near_channel_list(request):
    """
    这里有两种实现方式, 后续可以根据需求或数据量调整
    1. 先查找所有附近类型的房间，再查这些房间用户，算附近排序(现在使用中)
    2. 先直接查找附近n距离内的用户，再根据这些用户找到房间
    """
    channel_ids = Channel.objects.filter(channel_type=ChannelType.public.value).values_list("id", flat=True)
    user_ids = ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True)
    place = Place.get(user_id=request.user.id)
    channels = []
    if place:
        user_locations = Place.get_multi_user_dis(user_ids=user_ids)
        sorted_user_ids = sorted(user_locations.items(), key=lambda item: item[1])

        for user_id in sorted_user_ids:
            channel_id = ChannelMember.objects.filter(channel_type=ChannelType.normal.value,
                                                      user_id=user_id).values_list("channel_id", flat=True)
            channel = Channel.get_channel(channel_id=channel_id)
            if not channel:
                continue

            channels.append(channel.to_dict())

    limit = 100 - len(channels)
    channel_list = Channel.objects.filter(channel_type=ChannelType.public.value).order_by("-id")[:limit]
    for channel in channel_list:
        channels.append(channel.to_dict())

    return JsonResponse({"channels": channels})


def private_channel_list(request):
    # my_channel_id = Channel.objects.filter(user_id=request.user.id).values_list("channel_id", flat=True)
    channel_ids = InviteParty.objects.filter(party_type=ChannelType.private.value,
                                             to_user_id=request.user.id).values_list("channel_id", flat=True)
    # channel_ids = my_channel_id + channel_ids
    channels = [Channel.get_channel(channel_id=channel_id).to_dict() for channel_id in channel_ids]
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)

    friend_list = []
    for friend_id in friend_ids:
        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels, "friends": friend_list})


@login_required_404
def create_channel(request):
    channel_type = int(request.POST.get("channel_type", ChannelType.normal.value))

    try:
        ChannelType(channel_type)
    except ValueError:
        return HttpResponseBadRequest()

    channel = Channel.create_channel(user_id=request.user.id, channel_type=channel_type)
    if channel:
        InviteParty.clear(request.user.id)
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

    agora = Agora(user_id=request.user.id)
    channel_key = agora.get_channel_madia_key(channel_name=channel_id.encode("utf8"))

    channel = Channel.get_channel(channel_id=channel_id)
    if not channel:
        return HttpResponseBadRequest()

    if channel.is_lock:
        return JsonResponse({"is_lock": True})

    Channel.join_channel(channel_id=channel_id,
                         user_id=request.user.id)
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


def dirty_game_question(request):
    from .consts import DIRTY_GAME_QUESTIONS
    questions = DIRTY_GAME_QUESTIONS.split("\n")
    questions = [question for question in questions if question]
    question = random.sample(questions, 1)[0]
    channel_id = request.POST.get('channel_id', 'sayroom')

    kwargs = {
        "data": {
            "avatar_url": request.user.avatar_url,
            "nickname": request.user.nickname,
            "question": question,
            "time": int(time.time() * 1000),
        },
        "type": 2
    }

    try:
        agora = Agora(user_id=request.user.id)
        agora.send_cannel_msg(channel_id=channel_id, **kwargs)
    except:
        pass

    return JsonResponse({"question": question})
