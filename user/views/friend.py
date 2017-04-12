# -*- coding: utf-8 -*-

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.http import JsonResponse
from corelib.decorators import login_required_404
from corelib.leancloud import LeanCloud

from user.models import User, UserContact, InviteFriend, Friend, ContactError
from user.models import Ignore


def invite_friend(request):
    invited_id = request.POST.get("invited_id")
    is_success = InviteFriend.add(user_id=request.user.id, invited_id=invited_id)
    if is_success:
        # message = "%s 邀请你加入好友" % request.user.nickname
        # LeanCloud.async_push(receive_id=invited_id, message=message)
        return JsonResponse()
    return HttpResponseServerError()


def agree_friend(request):
    invited_id = request.POST.get("invited_id")
    is_success = InviteFriend.agree(user_id=request.user.id, invited_id=invited_id)
    if is_success:
        # message = "%s 同意了你的好友请求" % request.user.nickname
        # LeanCloud.async_push(receive_id=invited_id, message=message)
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
    return JsonResponse(friend_list)


def get_friend_invites(request):
    pass
