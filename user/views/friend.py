# -*- coding: utf-8 -*-
import random

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.http import JsonResponse
from corelib.decorators import login_required_404
from corelib.jiguang import JPush
from corelib.redis import redis

from user.models import User, UserContact, InviteFriend, Friend, ContactError
from user.models import Ignore, common_friends
from socket_server import SocketServer, EventType
from live.models import ChannelMember, Channel


@login_required_404
def invite_friend(request):
    from user.models import ChannelAddFriendLog
    invited_id = request.POST.get("invited_id")

    user1 = ChannelMember.objects.filter(user_id=invited_id).first()
    user2 = ChannelMember.objects.filter(user_id=request.user.id).first()
    if user1 and user2:
        if user1.channel_id == user2.channel_id:
            channel = Channel.objects.filter(channel_id=user1.channel_id).first()
            ChannelAddFriendLog.objects.create(user_id=request.user.id,
                                               friend_id=invited_id,
                                               channel_type=channel.channel_type)

    is_success = InviteFriend.add(user_id=request.user.id,
                                  invited_id=invited_id)
    if is_success:
        push_lock = redis.get("mc:user:%s:friend:%s:invite_push_lock" % (request.user.id, invited_id))
        if not push_lock:
            message = "%s 申请添加你为好友" % request.user.nickname
            JPush().async_push(user_ids=[invited_id], message=message)
            data = {
                "from_user_id": request.user.id,
                "avatar_url": request.user.avatar_url,
            }
            SocketServer().invite_friend(user_id=request.user.id,
                                         to_user_id=invited_id,
                                         message=message,
                                         **data)
            redis.set("mc:user:%s:friend:%s:invite_push_lock" % (request.user.id, invited_id), 1, 60)
        return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def agree_friend(request):
    invited_id = request.POST.get("invited_id")

    try:
        is_success = InviteFriend.agree(user_id=request.user.id,
                                        invited_id=invited_id)
    except:
        Friend.objects.filter(user_id=invited_id, friend_id=request.user.id).delete()
        Friend.objects.filter(user_id=request.user.id, friend_id=invited_id).delete()
        is_success = InviteFriend.agree(user_id=request.user.id,
                                        invited_id=invited_id)

    if is_success:
        message = "%s 通过了你的好友申请，一起开PA吧！" % request.user.nickname
        JPush().async_push(user_ids=[invited_id], message=message)
        SocketServer().agree_friend(user_id=request.user.id,
                                    to_user_id=invited_id,
                                    message=message)
        SocketServer().refresh(user_id=request.user.id,
                               to_user_id=[request.user.id, invited_id],
                               message="refresh",
                               event_type=EventType.refresh_friend.value)
        return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def delete_friend(request):
    friend_id = request.POST.get("friend_id")
    is_success = Friend.delete_friend(owner_id=request.user.id, friend_id=friend_id)
    if is_success:
        SocketServer().refresh(user_id=request.user.id,
                               to_user_id=[request.user.id, friend_id],
                               message="refresh",
                               event_type=EventType.refresh_friend.value)
        return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def get_friends_order_by_pinyin(request):
    friend_list = Friend.get_friends_order_by_pinyin(user_id=request.user.id)
    keys = list(friend_list.keys())
    has_other = "#" in keys

    if has_other:
        keys.remove("#")

    sorted_keys = sorted(keys)
    if has_other:
        sorted_keys.append("#")
    return JsonResponse({"friend_list": friend_list, "keys": sorted_keys})


@login_required_404
def update_user_memo(request):
    friend_id = request.POST.get("friend_id")
    memo = request.POST.get("memo")

    friend = Friend.objects.filter(user_id=request.user.id, friend_id=friend_id).first()
    if friend:
        is_success = friend.update_memo(memo=memo)
        if is_success:
            return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def update_invisible(request):
    friend_id = request.POST.get("friend_id")
    invisible = request.POST.get("invisible")

    if invisible is None:
        return HttpResponseBadRequest()

    friend = Friend.objects.filter(user_id=request.user.id, friend_id=friend_id).first()
    if friend:
        is_success = friend.update_invisible(is_invisible=int(invisible))
        if is_success:
            return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def update_push(request):
    friend_id = request.POST.get("friend_id")
    push = request.POST.get("push")

    if push is None:
        return HttpResponseBadRequest()

    friend = Friend.objects.filter(user_id=request.user.id, friend_id=friend_id).first()
    if friend:
        is_success = friend.update_push(is_push=int(push))
        if is_success:
            return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def who_is_friends(request):
    friend_ids = request.GET.get("friend_ids", "")
    friend_ids = friend_ids.split(",")

    friend_ids = Friend.who_is_friends(owner_id=request.user.id, friend_ids=friend_ids)
    return JsonResponse({"friend_ids": friend_ids})


@login_required_404
def unagree_friend_count(request):
    ignore_user_ids = list(Ignore.objects.filter(owner_id=request.user.id, ignore_type__in=[1, 3])
                                         .values_list("ignore_id", flat=True))
    count = InviteFriend.objects.filter(invited_id=request.user.id, status=0).exclude(user_id__in=ignore_user_ids).count()
    return JsonResponse({"unagree_count": count})


@login_required_404
def friend_relation(request):
    user_id = request.GET.get("user_id", "")
    common_friend_list = common_friends(user_id=request.user.id, to_user_id=user_id)
    is_friend = Friend.is_friend(owner_id=request.user.id, friend_id=user_id)
    common_friend = random.sample(common_friend_list, 1)[0] if common_friend_list else ""
    return JsonResponse({"is_friend": is_friend, "common_friend": common_friend})
