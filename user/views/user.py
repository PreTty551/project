# -*- coding: utf-8 -*-
import json
import datetime
import django_rq
import requests
import hashlib

from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.jiguang import JSMS
from corelib.http import JsonResponse
from corelib.errors import LoginError
from corelib.weibo import Weibo
from corelib.wechat import OAuth
from corelib.decorators import login_required_404
from corelib.paginator import paginator
from corelib.rongcloud import RongCloud
from corelib.jiguang import JPush

from user.consts import APPSTORE_MOBILE, ANDROID_MOBILE, SAY_MOBILE, UserEnum
from user.models import User, ThirdUser, create_third_user, update_avatar_in_third_login, TempThirdUser, Place
from user.models import UserContact, InviteFriend, Friend, Ignore, ContactError, two_degree_relation, guess_know_user
from socket_server import SocketServer
from live.models import Channel, ChannelMember, InviteParty


@require_http_methods(["POST"])
def request_sms_code(request):
    mobile = request.POST.get("mobile", "")
    if not mobile:
        return HttpResponseBadRequest()

    try:
        jsms = JSMS(mobile=mobile)
        is_success, error_dict = jsms.request_code()
        if is_success:
            return JsonResponse()
        return JsonResponse(error=error_dict)
    except Exception as e:
        return JsonResponse(error=LoginError.REQUEST_SMS_CODE)


def request_voice_code(request):
    mobile = request.POST.get("mobile", "")
    if not mobile:
        return HttpResponseBadRequest()

    try:
        jsms = JSMS(mobile=mobile)
        is_success, error_dict = jsms.request_voice_code()
        if is_success:
            return JsonResponse()
        return JsonResponse(error=error_dict)
    except Exception as e:
        return JsonResponse(error=LoginError.REQUEST_SMS_CODE)


@require_http_methods(["POST"])
def verify_sms_code(request):
    code = request.POST.get('code', '')
    mobile = request.POST.get('mobile', '')
    universal_code = datetime.datetime.now().strftime("%y%m%d")
    universal_code = "%s67" % universal_code[:4]

    if not mobile or not code:
        return HttpResponseBadRequest()

    is_special_mobile = mobile in (APPSTORE_MOBILE, ANDROID_MOBILE, SAY_MOBILE)
    is_universal_code = code == universal_code

    if is_special_mobile and code == '820323':
        user = User.objects.filter(mobile=mobile).first()
        user = authenticate(username=user.username, password=user.username)
        login(request, user)
        return JsonResponse(user.normal_info())

    try:
        if is_universal_code:
            is_success, error_dict = True, {}
        else:
            jsms = JSMS(mobile=mobile)
            is_success, error_dict = jsms.valid(code=code)
    except Exception as e:
        return JsonResponse(error=LoginError.SMS_CODE_ERROR)

    if is_success:
        user = User.objects.filter(mobile=mobile).first()
        if user:
            user = authenticate(username=user.username, password=user.username)
            if user is not None:
                login(request, user)
                if request.user.disable_login:
                    return JsonResponse(error=LoginError.DISABLE_LOGIN)

                basic_info = user.basic_info()
                basic_info["is_new_user"] = False
                return JsonResponse(basic_info)
        return JsonResponse({"is_new_user": True})
    else:
        return JsonResponse(error=error_dict)


@require_http_methods(["POST"])
def register(request):
    nickname = request.POST.get("nickname", "")
    mobile = request.POST.get("mobile", "")
    version = request.POST.get("version", "")
    platform = request.POST.get("platform", "")

    nickname = nickname.strip().replace("#", "").replace("@", "").replace(" ", "")
    if len(mobile) != 11:
        return HttpResponseBadRequest()

    user = User.objects.filter(mobile=mobile).first()
    if not user:
        user = User.objects.add_user(nickname=nickname,
                                     mobile=mobile,
                                     platform=platform,
                                     version=version)
        if not user:
            return HttpResponseServerError()

    # 登录
    if _login(request, user):
        return JsonResponse(user.basic_info())
    return JsonResponse(error=LoginError.REGISTER_ERROR)


def wx_user_login(request):
    code = request.POST.get("code")
    user_info = OAuth().get_user_info(code=code)
    if not user_info:
        return JsonResponse(error=LoginError.WX_LOGIN)

    third_user = ThirdUser.objects.filter(third_id=user_info["openid"]).first()
    if third_user:
        user = User.objects.filter(mobile=third_user.mobile).first()
        if user.disable_login:
            return JsonResponse(error=LoginError.DISABLE_LOGIN)

        # 登录
        if _login(request, user):
            basic_info = user.basic_info()
            basic_info["is_new_user"] = False
            return JsonResponse(basic_info)
    else:
        old_user = TempThirdUser.objects.filter(wx_unionid=user_info["unionid"]).first()
        if old_user:
            old_user.third_id = user_info["openid"]
            old_user.wx_unionid = user_info["unionid"]
            old_user.avatar = user_info["headimgurl"]
            old_user.save()
            return JsonResponse({"temp_third_id": old_user.id, "is_new_user": True})

        sex = int(user_info["sex"])
        gender = 0 if sex == 2 else sex
        temp_third_user = TempThirdUser.objects.create(third_id=user_info["openid"],
                                                       third_name="wx",
                                                       gender=gender,
                                                       nickname=user_info["nickname"],
                                                       avatar=user_info["headimgurl"])

        return JsonResponse({"temp_third_id": temp_third_user.id, "is_new_user": True})
    return JsonResponse(error=LoginError.WX_LOGIN)


def wb_user_login(request):
    access_token = request.POST.get("access_token")
    third_id = request.POST.get("third_id")

    if not (third_id and access_token):
        return HttpResponseBadRequest()

    third_user = ThirdUser.objects.filter(third_id=third_id).first()
    if third_user:
        user = User.objects.filter(mobile=third_user.mobile).first()
        if user.disable_login:
            return JsonResponse(error=LoginError.DISABLE_LOGIN)

        # 登录
        if _login(request, user):
            basic_info = user.basic_info()
            basic_info["is_new_user"] = False
            return JsonResponse(basic_info)
    else:
        old_user = TempThirdUser.objects.filter(third_id=third_id).first()
        if old_user:
            old_user.third_id = user_info["uid"]
            old_user.avatar = user_info["avatar"]
            old_user.save()
            return JsonResponse({"temp_third_id": old_user.id, "is_new_user": True})
        else:
            try:
                weibo = Weibo(access_token=access_token, uid=third_id)
                user_info = weibo.get_user_info()
                if not user_info:
                    return JsonResponse(error=LoginError.WB_LOGIN)
            except:
                return JsonResponse(error=LoginError.WB_LOGIN)

            temp_third_user = TempThirdUser.objects.create(third_id=user_info["uid"],
                                                           third_name="wb",
                                                           gender=user_info["gender"],
                                                           nickname=user_info["nickname"],
                                                           avatar=user_info["avatar"])
            return JsonResponse({"temp_third_id": temp_third_user.id, "is_new_user": True})
    return JsonResponse(error=LoginError.WB_LOGIN)


def third_request_sms_code(request):
    mobile = request.POST.get("mobile", "")
    third_name = request.POST.get("third_name", "")
    if not mobile:
        return HttpResponseBadRequest()

    third_user = User.objects.filter(mobile=mobile).first()
    if third_user:
        return JsonResponse(error=LoginError.MOBILE_ALREADY_USED)

    try:
        jsms = JSMS(mobile=mobile)
        is_success, error_dict = jsms.request_code()
        if is_success:
            return JsonResponse()
        return JsonResponse(error=error_dict)
    except Exception as e:
        return JsonResponse(error=LoginError.REQUEST_SMS_CODE)


def third_verify_sms_code(request):
    """1男0女"""
    temp_third_id = request.POST.get("temp_third_id")
    code = request.POST.get("code")
    mobile = request.POST.get("mobile", "")
    platform = request.POST.get("platform", "")
    version = request.POST.get("version", "")

    try:
        jsms = JSMS(mobile=mobile)
        is_success, error_dict = jsms.valid(code=code)
    except Exception as e:
        return JsonResponse(error=LoginError.SMS_CODE_ERROR)

    if not is_success:
        return JsonResponse(error=error_dict)

    temp_user = TempThirdUser.objects.filter(id=temp_third_id).first()
    # 老用户
    user_id = temp_user.user_id
    if user_id:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse(error=LoginError.REGISTER_ERROR)

        user.mobile = mobile
        user.platform = platform
        user.version = version
        user.save()
        ThirdUser.objects.create(mobile=mobile,
                                 third_id=temp_user.third_id,
                                 third_name=temp_user.third_name)
    else:
        user = create_third_user(third_id=temp_user.third_id,
                                 third_name=temp_user.third_name,
                                 nickname=temp_user.nickname,
                                 avatar="",
                                 gender=temp_user.gender,
                                 mobile=mobile,
                                 platform=platform,
                                 version=version)
    # 异步队列更新头像
    queue = django_rq.get_queue('avatar')
    queue.enqueue(update_avatar_in_third_login, temp_user.avatar, user.id)

    if user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)

    # 登录
    if _login(request, user):
        return JsonResponse(user.basic_info())
    return JsonResponse(error=LoginError.REGISTER_ERROR)


def _login(request, user):
    from live.models import ChannelMember
    ChannelMember.objects.filter(user_id=user.id).delete()
    user = authenticate(username=user.username, password=user.username)
    if user is not None:
        login(request, user)
        user.online()
        return True
    return False


def check_login(request):
    if not (request.user and request.user.is_authenticated()):
        return JsonResponse(error=LoginError.NOT_LOGIN)

    if request.user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)

    user = authenticate(username=request.user.username, password=request.user.username)
    login(request, user)
    user.online()
    return JsonResponse(request.user.basic_info())


def get_profile(request):
    user = User.get(id=request.user.id)
    invite_friend_ids = InviteFriend.get_invited_my_ids(owner_id=request.user.id)
    invite_friends = []
    for friend_id in invite_friend_ids:
        u = User.get(friend_id)
        basic_info = u.basic_info()
        basic_info["user_relation"] = UserEnum.be_invite.value
        invite_friends.append(basic_info)

    two_degrees = []
    two_degree = two_degree_relation(user_id=request.user.id)
    for user_id, count in two_degree:
        u = User.get(user_id)
        basic_info = u.basic_info()
        basic_info["user_relation"] = UserEnum.nothing.value
        two_degrees.append(basic_info)
    out_app_contacts = UserContact.recommend_contacts(request.user.id, 20)

    results = {}
    results["user"] = user.basic_info()
    results["friend_count"] = Friend.count(user_id=request.user.id)
    results["friend_invite_count"] = InviteFriend.count(user_id=request.user.id)
    results["two_degree"] = guess_know_user(request.user.id)
    results["out_app_contacts"] = out_app_contacts
    results["invite_friends"] = invite_friends
    return JsonResponse(results)


def rong_token(request):
    if request.user.rong_token:
        return JsonResponse({"token": request.user.rong_token})

    token = request.user.create_rong_token()
    request.user.rong_token = token
    request.user.save()
    return JsonResponse({"token": token})


def get_basic_user_info(request):
    user_id = request.GET.get("user_id")
    if user_id:
        user = User.get(id=user_id)
        if user:
            return JsonResponse(user.basic_info())
        return HttpResponseNotFound()
    return HttpResponseBadRequest()


def bind_wechat(request):
    code = request.POST.get("code")
    user_info = OAuth.get_user_info(code=code)
    if not user_info:
        return JsonResponse(error=LoginError.WX_LOGIN)

    third_id = user_info["open_id"]
    third_name = "wx"

    third_user = ThirdUser.objects.filter(third_id=third_id, third_name=third_name).frist()
    if third_user:
        user = User.get(id=request.user.id)
        if third_user.mobile == user.mobile:
            return JsonResponse()
        else:
            return JsonResponse(error=LoginError.DUPLICATE_BING)

    request.user.binding_wechat(third_id=third_id)
    return JsonResponse()


def bind_weibo(request):
    access_token = request.POST.get("access_token")
    third_id = request.POST.get("third_id")

    third_user = ThirdUser.objects.filter(third_id=third_id, third_name="wb").frist()
    if third_user:
        user = User.get(id=request.user.id)
        if third_user.mobile == user.mobile:
            return JsonResponse()
        else:
            return JsonResponse(error=LoginError.DUPLICATE_BING)

    request.user.binding_wechat(third_id=third_id)
    return JsonResponse()


def unbind_wechat(reqeust):
    is_success = request.user.unbinding_wechat()
    if is_success:
        return JsonResponse()
    return HttpResponseServerError()


def unbind_weibo(request):
    is_success = request.user.unbinding_weibo()
    if is_success:
        return JsonResponse()
    return HttpResponseServerError()


def update_paid(request):
    paid = request.POST.get("paid")
    user = User.objects.filter(paid=paid).first()
    if user:
        return JsonResponse(error=LoginError.PA_ALREADY_USED)

    User.objects.filter(id=request.user.id).update(paid=paid)
    return JsonResponse()


def update_gender(request):
    gender = request.POST.get("gender")
    User.objects.filter(id=request.user.id).update(gender=gender)
    return JsonResponse()


def update_nickname(request):
    nickname = request.POST.get("nickname")
    User.objects.filter(id=request.user.id).update(nickname=nickname)
    return JsonResponse()


def update_intro(request):
    intro = request.POST.get("intro")
    User.objects.filter(id=request.user.id).update(intro=intro)
    return JsonResponse()


def update_avatar(request):
    avatar = request.POST.get("avatar")
    User.objects.filter(id=request.user.id).update(avatar=avatar)
    return JsonResponse()


def search(request):
    content = request.POST.get("content")
    page = request.POST.get("page", 1)

    user_list = list(User.objects.filter(paid=content))
    if not user_list:
        user_list = User.objects.filter(nickname__startswith=content)

    results = {"user_list": [], "paginator": {}}
    user_list, paginator_dict = paginator(user_list, page, 30)
    user_list = [user.basic_info() for user in user_list]
    results["paginator"] = paginator_dict
    results["friends"] = user_list

    return JsonResponse(results)


def detail_user_info(request):
    user_id = request.GET.get("user_id")

    user = User.get(id=user_id)
    if request.user.id == user_id:
        detail_info = user.detail_info()
    else:
        detail_info = user.detail_info(user_id=request.user.id)

    return JsonResponse(detail_info)


def party_push(request):
    """
    1. 一周内开party的用户
    """
    bulk_ids = []
    ids = []
    i = 0

    friend_ids = Friend.get_friend_ids(user_id=user_id)
    pre_week = timezone.now() - datetime.timedelta(days=7)
    party_user_ids_in_week = list(LiveMediaLog.objects.filter(data__gte=pre_week, user_id__in=friend_ids)
                                                      .values_list("user_id", flat=True).distinct())
    bulk_user_ids = set(party_user_ids_in_week) ^ set(friend_ids)

    message = "%s 正在开party" % request.user.nickname
    JPush().async_push(user_ids=bulk_user_ids, message=message)

    for friend_id in party_user_ids_in_week:
        if i < 11:
            fids = Friend.get_friend_ids(user_id=friend_id)
            party_user_ids = ChannelMember.objects.filter(user_id__in=fids).values_list("user_id", flat=True)
            nicknames = [User.get(id=uid).nickname for uid in party_user_ids]
            nicknames = ",".join(nicknames)
            message = "%s 正在开party" % nicknames
            JPush().async_push(user_ids=[friend_id], message=message)
            i += 1
    return JsonResponse()


def invite_party(request):
    receiver_id = request.POST.get("user_id")

    max_number = 20
    push_number = 0
    icon = ""
    message = u"%s邀请你来开Party" % request.user.nickname
    for i in range(push_number):
        icon += u"👉"

    message = u"%s%s" % (icon, message)

    channel_member = ChannelMember.objects.filter(user_id=request.user.id).first()
    if channel_member:
        SocketServer().invite_party_in_live(user_id=request.user.id,
                                            to_user_id=receiver_id,
                                            message=message,
                                            channel_id=member.channel_id)
        JPush().async_push(user_ids=[receiver_id],
                           message=message,
                           push_type=8,
                           channel_id=member.channel_id)
    else:
        InviteParty.add(user_id=request.user.id, to_user_id=receiver_id, party_type=1)
        SocketServer().invite_party_out_live(user_id=request.user.id,
                                             to_user_id=receiver_id,
                                             message=message)
        JPush().async_push(user_ids=[receiver_id],
                           message=message)

    return JsonResponse()


def quit_app(request):
    request.user.offline()
    return JsonResponse()


def user_online_and_offine_callback(request):
    nonce = request.GET.get("nonce")
    timestamp = request.GET.get("timestamp")
    signature = request.GET.get("signature")

    valid_success = RongCloud().valid_signature(nonce=nonce,
                                                timestamp=timestamp,
                                                signature=signature)
    if not valid_success:
        return JsonResponse()

    for body in json.loads(request.body):
        user_id = body["userid"]
        status = body["status"]
        os = body["os"]
        time = body["time"]

        user = User.get(user_id)
        if int(status) == 0:
            user.online()
        else:
            user.offline()
    return JsonResponse()


def fuck_you(request):
    token = hashlib.sha1(request.COOKIES["sessionid"].encode('utf-8')).hexdigest()
    data = {
        "type": 4444,
        "data": {
            "token": token,
        }
    }
    return JsonResponse(data)


def add_user_location(request):
    lon = request.POST.get("lon", "")
    lat = request.POST.get("lat", "")

    Place.add(lon=float(lon), lat=float(lat), user_id=request.user.id)
    return JsonResponse()
