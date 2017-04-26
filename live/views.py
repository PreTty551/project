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
from corelib.redis import redis

from live.models import Channel, ChannelMember, GuessWord, InviteChannel, InviteParty
from live.consts import ChannelType
from user.models import User, Friend, UserContact, Place, guess_know_user, friend_dynamic
from user.consts import UserEnum

TEST_USER_IDS = []


def refresh_list(request):
    channels = []
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
            basic_info["is_hint"] = False
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels,
                         "friends": friend_list})


def refresh_home_list(request):
    channels = []

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
            basic_info["is_hint"] = False
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    return JsonResponse({"channels": channels,
                         "friends": friend_list})


@login_required_404
def home_list(request):
    """
    首页房间列表，包含
       1. 我的好友开的public party
       2. 好友可见的party
    """
    channels = []

    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    channel_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("channel_id", flat=True).distinct()
    for channel_id in channel_ids:
        channel = Channel.get_channel(channel_id)
        if not channel:
            continue
        if channel.channel_type == ChannelType.private.value:
            continue
        channels.append(channel.to_dict())

    # 红点, 排序
    invite_party_ids = InviteParty.get_invites(user_id=request.user.id)
    friend_list = []
    for user_id in invite_party_ids:
        user = User.get(id=user_id)
        if user:
            basic_info = user.basic_info()
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["is_hint"] = True
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    guess_know_user = guess_know_user(request.user.id)
    if len(guess_know_user) < 5:
        guess_contacts =
    else:
        guess_contacts = UserContact.recommend_contacts(request.user.id, 20)
    return JsonResponse({"channels": channels,
                         "friends": friend_list,
                         "guess_know_users": guess_know_user,
                         "guess_contacts": guess_contacts})


@login_required_404
def livemedia_list(request):
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    channel_ids = ChannelMember.objects.filter(user_id__in=friend_ids).values_list("channel_id", flat=True).distinct()
    channels = []
    channel = Channel.objects.filter(creator_id=request.user.id).first()
    if channel:
        channels.append(channel.to_dict())

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
            basic_info["dynamic"] = friend_dynamic(user.id)
            friend_list.append(basic_info)

    for friend_id in friend_ids:
        if friend_id in invite_party_ids:
            continue

        user = User.get(id=friend_id)
        if user:
            basic_info = user.basic_info()
            basic_info["is_hint"] = False
            basic_info["user_relation"] = UserEnum.friend.value
            basic_info["dynamic"] = friend_dynamic(user.id)
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
    channel_ids = list(Channel.objects.filter(channel_type=ChannelType.public.value).values_list("id", flat=True))
    user_ids = list(ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True))
    place = Place.get(user_id=request.user.id)
    channels = []
    if place:
        user_locations = place.get_multi_user_dis(user_ids=user_ids)
        if user_locations:
            sorted_user_ids = sorted(user_locations.items(), key=lambda item: item[1])

            for user_id in sorted_user_ids:
                channel_member = ChannelMember.objects.filter(channel_type=ChannelType.normal.value,
                                                              user_id=user_id).frist()
                channel = Channel.get_channel(channel_id=channel_member.channel_id)
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
    channels = []
    for channel_id in channel_ids:
        channel = Channel.get_channel(channel_id=channel_id)
        if channel:
            channels.append(channel.to_dict())

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

    InviteParty.clear(request.user.id)
    channel = Channel.create_channel(user_id=request.user.id, channel_type=channel_type)
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
        "data": {
            "user_id": request.user.id,
            "content": GuessWord.get_random_word()
        }
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
        "data": {
            "user_id": request.user.id,
        }
    }

    agora = Agora(user_id=request.user.id)
    agora.send_cannel_msg(channel_id=channel_id, **data)
    return JsonResponse()


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


def poke(request):
    user_id = request.POST.get("user_id")

    push_lock = redis.get("mc:user:%s:to_user_id:%s:poke_lock" % (request.user.id, user_id)) or 0
    if push_lock and int(push_lock) <= 20:
        icon = ""
        message = u"%s捅了你一下" % request.user.nickname
        for i in range(push_lock):
            icon += u"👉"
        message = u"%s%s" % (icon, message)

        SocketServer().invite_party_in_live(user_id=request.user.id,
                                            to_user_id=receiver_id,
                                            message=message,
                                            channel_id=0)

        redis.set("mc:user:%s:to_user_id:%s:poke_lock" % (request.user.id, user_id), int(push_lock) + 1, 600)
    return JsonResponse()
