# -*- coding: utf-8 -*-
import time
import random
import requests
import datetime

from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from corelib.decorators import login_required_404
from corelib.agora import Agora
from corelib.http import JsonResponse
from corelib.websocket import Websocket
from corelib.redis import redis

from live.models import Channel, ChannelMember, GuessWord, InviteParty, LiveMediaLog, party_push, refresh, LiveLockLog
from live.consts import ChannelType, MC_PA_PUSH_LOCK
from user.models import User, Friend, UserContact, Place, guess_know_user, UserDynamic
from user.consts import UserEnum
from ida.models import Duty
from widget import FriendListWidget, ChannelListWidget, ChannelInnerListWidget

TEST_USER_IDS = []


@login_required_404
def home_list(request):
    friend_list = FriendListWidget.list(user_id=request.user.id)
    channel_list = ChannelListWidget.list(user_id=request.user.id)

    _guess_know_user = guess_know_user(request.user.id)
    if len(_guess_know_user) < 5:
        guess_contacts = UserContact.get_contacts_out_app(request.user.id)
    else:
        guess_contacts = UserContact.recommend_contacts(request.user.id, 20)
    return JsonResponse({"channels": channel_list,
                         "friends": friend_list,
                         "guess_know_users": _guess_know_user,
                         "guess_contacts": guess_contacts})


@login_required_404
def refresh_home_list(request):
    friend_list = FriendListWidget.list(user_id=request.user.id)
    channel_list = ChannelListWidget.list(user_id=request.user.id)

    return JsonResponse({"channels": channel_list,
                         "friends": friend_list})


@login_required_404
def channel_inner_list(request):
    friend_list = FriendListWidget.list(user_id=request.user.id)
    channel_list = ChannelInnerListWidget.list(user_id=request.user.id)

    _guess_know_user = guess_know_user(request.user.id)
    if len(_guess_know_user) < 5:
        guess_contacts = UserContact.get_contacts_out_app(request.user.id)
    else:
        guess_contacts = UserContact.recommend_contacts(request.user.id, 20)
    return JsonResponse({"channels": channel_list,
                         "friends": friend_list,
                         "guess_know_users": _guess_know_user,
                         "guess_contacts": guess_contacts})


@login_required_404
def refresh_list(request):
    friend_list = FriendListWidget.list(user_id=request.user.id)
    channel_list = ChannelInnerListWidget.list(user_id=request.user.id)

    return JsonResponse({"channels": channel_list,
                         "friends": friend_list})


@login_required_404
def near_channel_list(request):
    """
    这里有两种实现方式, 后续可以根据需求或数据量调整
    1. 先查找所有附近类型的房间，再查这些房间用户，算附近排序(现在使用中)
    2. 先直接查找附近n距离内的用户，再根据这些用户找到房间
    """
    # channel_ids = list(Channel.objects.filter(channel_type=ChannelType.public.value).values_list("id", flat=True))
    # user_ids = list(ChannelMember.objects.filter(channel_id__in=channel_ids).values_list("user_id", flat=True))
    # place = Place.get(user_id=request.user.id)
    # channels = []
    # if place:
    #     user_locations = place.get_multi_user_dis(user_ids=user_ids)
    #     if user_locations:
    #         sorted_user_ids = sorted(user_locations.items(), key=lambda item: item[1])
    #
    #         for user_id in sorted_user_ids:
    #             channel_member = ChannelMember.objects.filter(channel_type=ChannelType.normal.value,
    #                                                           user_id=user_id).frist()
    #             channel = Channel.get_channel(channel_id=channel_member.channel_id)
    #             if not channel:
    #                 continue
    #
    #             channels.append(channel.to_dict())
    # limit = 100 - len(channels)

    friend_ids = Friend.get_friend_ids(user_id=request.user.id)

    # 兼职人员互相看不到
    ignore_channel_ids = []
    ignore_user_ids = Duty.objects.values_list("user_id", flat=True)
    if request.user.id in ignore_user_ids:
        ignore_channel_ids = ChannelMember.objects.filter(channel_type=ChannelType.public.value,
                                                          user_id__in=ignore_user_ids) \
                                                  .values_list("channel_id", flat=True)

    friend_channel_ids = list(ChannelMember.objects.filter(user_id__in=friend_ids,
                                                           channel_type=ChannelType.public.value)
                                                   .values_list("channel_id", flat=True))

    limit = 100 - len(set(friend_channel_ids))
    public_channel_ids = list(Channel.objects.filter(channel_type=ChannelType.public.value)
                                             .exclude(id__in=friend_channel_ids)
                                             .order_by("?").values_list("channel_id", flat=True)[:limit])

    public_channel_ids.extend(friend_channel_ids)
    public_channel_ids = list(set(public_channel_ids))

    member_list = ChannelMember.objects.filter(channel_id__in=public_channel_ids)

    members = []
    members_dict = {}
    channel_user_ids = []
    for member in member_list:
        _ = members_dict.setdefault(member.channel_id, [])
        _.append((member.user_id, member.nickname))
        channel_user_ids.append(member.user_id)

    channels = []
    public_channel_ids = [channel_id for channel_id in public_channel_ids if channel_id not in ignore_channel_ids]
    channel_list = Channel.objects.filter(channel_id__in=public_channel_ids)
    for channel in channel_list:
        member = members_dict.get(channel.channel_id)
        if not member:
            continue

        friend_nicknames = []
        user_icon = None
        for user_id, nickname in member:
            if user_id in friend_ids:
                user_icon = user_id
                friend_nicknames.append((nickname, 0))
            else:
                friend_nicknames.append((nickname, 1))

            if not user_icon:
                user_icon = user_id

        friend_nicknames = sorted(friend_nicknames, key=lambda item: item[1])
        user = User.get(user_icon)
        icon = user.avatar_url
        channels.append(channel.to_dict(nicknames=friend_nicknames, icon=icon))

    friend_list = FriendListWidget.list(user_id=request.user.id)
    return JsonResponse({"channels": channels, "friends": friend_list})


@login_required_404
def create_channel(request):
    channel_type = int(request.POST.get("channel_type", ChannelType.normal.value))

    try:
        ChannelType(channel_type)
    except ValueError:
        return HttpResponseBadRequest()

    channel = Channel.create_channel(user_id=request.user.id,
                                     channel_type=channel_type,
                                     nickname=request.user.nickname)
    if channel:
        UserDynamic.update_dynamic(user_id=request.user.id, paing=channel_type)
        party_push(user_id=request.user.id,
                   channel_id=channel.channel_id,
                   channel_type=channel.channel_type)

        agora = Agora(user_id=request.user.id)
        channel_key = agora.get_channel_madia_key(channel_name=channel.channel_id)
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

    UserDynamic.update_dynamic(user_id=request.user.id, paing=channel.channel_type)
    if channel.is_lock:
        return JsonResponse({"is_lock": True})

    Channel.join_channel(channel_id=channel_id,
                         channel_type=channel.channel_type,
                         user_id=request.user.id,
                         nickname=request.user.nickname)

    return JsonResponse({"channel_id": channel_id, "channel_key": channel_key})


@require_http_methods(["POST"])
@login_required_404
def quit_channel(request):
    channel_id = request.POST.get("channel_id")
    content = request.POST.get("content", "")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        is_success = channel.quit_channel(user_id=request.user.id)
        if is_success:
            ud = UserDynamic.objects.filter(user_id=request.user.id).first()
            if ud:
                last_pa_time = ud.last_pa_time
                ud.paing = False
                ud.last_pa_time = timezone.now()
                ud.save()
                refresh(user_id=request.user.id, channel_type=channel.channel_type)

                if (timezone.now() - last_pa_time).seconds > 300:
                    return JsonResponse({"feedback": True})
        return JsonResponse({"feedback": False})
    return HttpResponseServerError()


@require_http_methods(["POST"])
@login_required_404
def delete_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.delete_channel()
        refresh(user_id=request.user.id, channel_type=channel.channel_type)
        return JsonResponse()
    return HttpResponseServerError()


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
        request.user.offline()

    return JsonResponse()


@require_http_methods(["POST"])
@login_required_404
def lock_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.lock()
        member_count = ChannelMember.objects.filter(channel_id=channel_id).count()
        LiveLockLog.objects.create(channel_id=channel_id,
                                   member_count=member_count)
        data = {
            "type": 6,
            "data": {
                "is_lock": True,
            }
        }
        agora = Agora(user_id=request.user.id)
        agora.send_cannel_msg(channel_id=channel_id, **data)
        return JsonResponse()
    return HttpResponseBadRequest()


@require_http_methods(["POST"])
@login_required_404
def unlock_channel(request):
    channel_id = request.POST.get("channel_id")
    channel = Channel.get_channel(channel_id=channel_id)
    if channel:
        channel.unlock()
        LiveLockLog.objects.filter(channel_id=channel_id, status=0) \
                           .update(end_date=timezone.now(), status=1)
        data = {
            "type": 6,
            "data": {
                "is_lock": False,
            }
        }
        agora = Agora(user_id=request.user.id)
        agora.send_cannel_msg(channel_id=channel_id, **data)
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

    push_role = request.user.push_role(friend_id=user_id)
    if not push_role:
        return JsonResponse()

    push_lock = redis.get("mc:user:%s:to_user_id:%s:poke_lock" % (request.user.id, user_id)) or 0
    if int(push_lock) <= 20:
        icon = ""
        message = u"%s捅了你一下" % request.user.nickname
        for i in list(range(int(push_lock))):
            icon += u"👉"
        message = u"%s%s" % (icon, message)

        SocketServer().invite_party_in_live(user_id=request.user.id,
                                            to_user_id=receiver_id,
                                            message=message,
                                            channel_id=0)

        redis.set("mc:user:%s:to_user_id:%s:poke_lock" % (request.user.id, user_id), int(push_lock) + 1, 600)
    return JsonResponse()


def bg(request):
    member = ChannelMember.objects.filter(user_id=request.user.id).first()
    if member:
        log = LiveMediaLog.objects.filter(user_id=request.user.id,
                                          channel_id=member.channel_id,
                                          type=2, status=1).first()
        if log:
            log.status = 2
            log.end_date = timezone.now()
            log.save()
            return JsonResponse()

        channel = Channel.get_channel(channel_id=member.channel_id)
        if channel:
            LiveMediaLog.objects.create(user_id=request.user.id,
                                        channel_id=member.channel_id,
                                        channel_type=channel.channel_type,
                                        type=2,
                                        status=1)
        return JsonResponse()
    return JsonResponse()
