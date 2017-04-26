# -*- coding: utf-8 -*-
import json

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.http import JsonResponse
from corelib.decorators import login_required_404

from user.consts import APPSTORE_MOBILE, ANDROID_MOBILE, SAY_MOBILE
from user.models import User, UserContact, InviteFriend, Friend, ContactError


def get_contacts(request):
    contact_list = UserContact.get_all_contact(user_id=request.user.id)
    return JsonResponse(contact_list)


def get_contact_list(request):
    contacts = UserContact.get_all_contact(user_id=request.user.id)
    all_mobile_list = list(UserContact.objects.filter(user_id=request.user.id).values_list("mobile", flat=True))
    friend_ids = Friend.get_friend_ids(user_id=request.user.id)
    user_ids = list(User.objects.filter(mobile__in=all_mobile_list)
                                .exclude(id__in=friend_ids)
                                .values_list("id", flat=True))

    contacts_in_app = []
    for user_id in user_ids:
        user = User.get(id=user_id)
        basic_info = user.basic_info()
        basic_info["user_relation"] = user.check_friend_relation(user_id=request.user.id)
        contacts_in_app.append(basic_info)

    return JsonResponse({"contacts": contacts, "contacts_in_app": contacts_in_app})


@login_required_404
def add_user_contact(request):
    contact = request.POST.get("contact")
    contact_list = json.loads(contact)
    is_success = UserContact.bulk_add(contact_list=contact_list, user_id=request.user.id)
    if is_success:
        user = User.get(request.user.id)
        user.is_contact = 1
        user.save()
        return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def update_user_contact(request):
    contact = request.POST.get("contact")
    contact_list = json.loads(contact)
    contact_list = UserContact.clean_contact(contact_list=contact_list)
    my_all_contact = UserContact.get_all_contact(user_id=request.user.id)
    new_contact_list = [o for o in contact_list if o not in my_all_contact]
    for uc in new_contact_list:
        obj = UserContact.objects.filter(user_id=request.user.id, mobile=uc["mobile"]).first()
        if obj:
            obj.name = uc["name"]
            obj.save()
        else:
            UserContact.objects.create(name=uc["name"],
                                       mobile=uc["mobile"],
                                       user_id=request.user.id)
    return JsonResponse()


def common_contact(request):
    mobile = request.GET.get("mobile", "")
    count = UserContact.objects.filter(mobile=mobile).count()
    return JsonResponse({"common_contact": "你们有%s个共同朋友" % count, "count": count})
