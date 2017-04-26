# -*- coding: utf-8 -*-

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.http import JsonResponse
from corelib.decorators import login_required_404
from corelib.jiguang import JPush

from user.models import User, UserContact, InviteFriend, Friend, ContactError
from user.models import Ignore
from socket_server import SocketServer, EventType


def invite_friend(request):
    invited_id = request.POST.get("invited_id")
    if InviteFriend.objects.filter(user_id=invited_id, invited_id=request.user.id).first():
        Friend.add(user_id=request.user.id, friend_id=invited_id)
    else:
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


def agree_friend(request):
    invited_id = request.POST.get("invited_id")
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


def ignore(request):
    user_id = request.POST.get("user_id")
    ignore_type = request.POST.get("ignore_type")
    ignore = Ignore.add(owner_id=request.user.id, user_id=user_id, ignore_type=ignore_type)
    if ignore:
        return JsonResponse()
    return HttpResponseServerError()


def get_friends(request):
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    friend_list = [User.get(user_id=friend_id).to_dict() for friend_id in friend_ids]
    return JsonResponse(friend_list)


def get_friends_order_by_pinyin(request):
    friend_list = Friend.get_friends_order_by_pinyin(user_id=request.user.id)
    keys = list(friend_list.keys())
    if "#" in keys:
        keys.remove("#")

    sorted_keys = sorted(keys)
    if "#" in keys:
        sorted_keys.append("#")
    return JsonResponse({"friend_list": friend_list, "keys": sorted_keys})


def update_user_memo(request):
    friend_id = request.POST.get("friend_id")
    memo = request.POST.get("memo")

    friend = Friend.objects.filter(user_id=request.user.id, friend_id=friend_id).first()
    if friend:
        is_success = friend.update_memo(memo=memo)
        if is_success:
            return JsonResponse()
    return HttpResponseServerError()


def update_invisible(request):
    friend_id = request.POST.get("friend_id")
    invisible = request.POST.get("invisible")

    friend = Friend.objects.filter(user_id=request.user.id, friend_id=friend_id).first()
    if friend:
        is_success = friend.update_invisible(is_invisible=invisible)
        if is_success:
            return JsonResponse()
    return HttpResponseServerError()


def update_push(request):
    friend_id = request.POST.get("friend_id")
    push = request.POST.get("push")

    friend = Friend.objects.filter(user_id=request.user.id, friend_id=friend_id).first()
    if friend:
        is_success = friend.update_push(is_push=push)
        if is_success:
            return JsonResponse()
    return HttpResponseServerError()


def who_is_friends(request):
    friend_ids = request.GET.get("friend_ids", "")
    friend_ids = friend_ids.split(",")

    friend_ids = Friend.who_is_friends(owner_id=request.user.id, friend_ids=friend_ids)
    return JsonResponse({"friend_ids": friend_ids})


def unagree_friend_count(request):
    count = InviteFriend.objects.filter(invited_id=request.user.id).count()
    return JsonResponse({"unagree_count": count})
