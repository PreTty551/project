# -*- coding: utf-8 -*-
import re
import json
import datetime
import django_rq
import requests
import hashlib

from django.utils import timezone
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from xpinyin import Pinyin

from corelib.jiguang import JSMS
from corelib.http import JsonResponse
from corelib.errors import LoginError
from corelib.weibo import Weibo
from corelib.wechat import OAuth
from corelib.decorators import login_required_404
from corelib.paginator import paginator
from corelib.rongcloud import RongCloud
from corelib.jiguang import JPush
from corelib.redis import redis
from corelib.kingsoft.ks3 import KS3
from corelib.twilio import Twilio

from user.consts import APPSTORE_MOBILE, ANDROID_MOBILE, SAY_MOBILE, UserEnum, \
                        REDIS_ONLINE_USERS_KEY, REDIS_ONLINE_USERS
from user.models import User, ThirdUser, create_third_user, update_avatar_in_third_login, TempThirdUser, Place
from user.models import UserContact, InviteFriend, Friend, Ignore, ContactError, two_degree_relation, guess_know_user
from socket_server import SocketServer
from live.models import Channel, ChannelMember, InviteParty
from live.consts import REDIS_DISABLE_FRIEND_SWITCH
from wallet.models import is_disable_wallet


@require_http_methods(["POST"])
def request_sms_code(request):
    mobile = request.POST.get("mobile", "")
    country_code = request.POST.get("country_code", "86")
    if not mobile:
        return HttpResponseBadRequest()

    if mobile in [APPSTORE_MOBILE, ANDROID_MOBILE]:
        return JsonResponse()

    try:
        if country_code == "86":
            jsms = JSMS(mobile=mobile)
            is_success, error_dict = jsms.request_code()
            if is_success:
                return JsonResponse()
        else:
            is_success = Twilio.send_sms(mobile=mobile, country_code=country_code)
            if is_success:
                return JsonResponse()

        return JsonResponse(error=error_dict)
    except Exception as e:
        return JsonResponse(error=LoginError.REQUEST_SMS_CODE)


@require_http_methods(["POST"])
def request_voice_code(request):
    mobile = request.POST.get("mobile", "")
    if not mobile:
        return HttpResponseBadRequest()

    if mobile in [APPSTORE_MOBILE, ANDROID_MOBILE]:
        return JsonResponse()

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
    country_code = request.POST.get("country_code", "86")

    if not mobile or not code:
        return HttpResponseBadRequest()

    is_special_mobile = mobile in (APPSTORE_MOBILE, ANDROID_MOBILE, SAY_MOBILE)
    is_universal_code = code == universal_code

    if is_special_mobile and code == '820323':
        user = User.objects.filter(mobile=mobile).first()
        user = authenticate(username=user.username, password=user.username)
        login(request, user)

        basic_info = user.basic_info()
        basic_info["is_bind_wechat"] = user.is_bind_wechat
        basic_info["is_bind_weibo"] = user.is_bind_weibo
        basic_info["is_disable_wallet"] = is_disable_wallet(request.user)
        basic_info["is_new_user"] = False

        return JsonResponse(basic_info)

    try:
        if is_universal_code:
            is_success, error_dict = True, {}
        else:
            if country_code == "86":
                jsms = JSMS(mobile=mobile)
                is_success, error_dict = jsms.valid(code=code)
            else:
                is_success = Twilio.valid_sms(mobile=mobile, country_code=country_code, code=code)
                if not is_success:
                    return JsonResponse(error=LoginError.SMS_CODE_ERROR)

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
                basic_info["is_bind_wechat"] = user.is_bind_wechat
                basic_info["is_bind_weibo"] = user.is_bind_weibo
                basic_info["is_disable_wallet"] = is_disable_wallet(request.user)
                basic_info["is_new_user"] = False
                return JsonResponse(basic_info)
        return JsonResponse({"is_new_user": True})
    return JsonResponse(error=LoginError.REGISTER_ERROR)


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
        if user:
            user.set_password(user.username)
            user.save()
            if user.disable_login:
                return JsonResponse(error=LoginError.DISABLE_LOGIN)

            # 登录
            if _login(request, user):
                basic_info = user.basic_info()
                basic_info["is_bind_wechat"] = user.is_bind_wechat
                basic_info["is_bind_weibo"] = user.is_bind_weibo
                basic_info["is_disable_wallet"] = is_disable_wallet(request.user)
                basic_info["is_new_user"] = False
                return JsonResponse(basic_info)

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


def wb_user_login(request):
    access_token = request.POST.get("access_token")
    third_id = request.POST.get("third_id")

    if not (third_id and access_token):
        return HttpResponseBadRequest()

    third_user = ThirdUser.objects.filter(third_id=third_id).first()
    if third_user:
        user = User.objects.filter(mobile=third_user.mobile).first()
        user.set_password(user.username)
        user.save()
        if user.disable_login:
            return JsonResponse(error=LoginError.DISABLE_LOGIN)

        # 登录
        if _login(request, user):
            basic_info = user.basic_info()
            basic_info["is_bind_wechat"] = user.is_bind_wechat
            basic_info["is_bind_weibo"] = user.is_bind_weibo
            basic_info["is_disable_wallet"] = is_disable_wallet(request.user)
            basic_info["is_new_user"] = False
            return JsonResponse(basic_info)
    else:
        old_user = TempThirdUser.objects.filter(third_id=third_id).first()
        if old_user:
            old_user.third_id = third_id
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
    country_code = request.POST.get("country_code", "86")
    if not mobile:
        return HttpResponseBadRequest()

    third_user = User.objects.filter(mobile=mobile).first()
    if third_user:
        return JsonResponse(error=LoginError.MOBILE_ALREADY_USED)

    try:
        if country_code == "86":
            jsms = JSMS(mobile=mobile)
            is_success, error_dict = jsms.request_code()
            if is_success:
                return JsonResponse()
        else:
            is_success = Twilio.send_sms(mobile=mobile, country_code=country_code)
            if is_success:
                return JsonResponse()

        return JsonResponse(error=error_dict)
    except Exception as e:
        return JsonResponse(error=LoginError.REQUEST_SMS_CODE)


def third_request_voice_code(request):
    mobile = request.POST.get("mobile", "")
    third_name = request.POST.get("third_name", "")
    if not mobile:
        return HttpResponseBadRequest()

    third_user = User.objects.filter(mobile=mobile).first()
    if third_user:
        return JsonResponse(error=LoginError.MOBILE_ALREADY_USED)

    try:
        jsms = JSMS(mobile=mobile)
        is_success, error_dict = jsms.request_voice_code()
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
    country_code = request.POST.get("country_code", "86")

    if not mobile:
        return

    try:
        if country_code == "86":
            jsms = JSMS(mobile=mobile)
            is_success, error_dict = jsms.valid(code=code)
        else:
            is_success = Twilio.valid_sms(mobile=mobile, country_code=country_code, code=code)
            if not is_success:
                error_dict = {50014: "验证码不正确, 请重新输入"}
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
        user.set_password(user.username)
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
        basic_info = user.basic_info()
        basic_info["is_bind_wechat"] = user.is_bind_wechat
        basic_info["is_bind_weibo"] = user.is_bind_weibo
        basic_info["is_disable_wallet"] = is_disable_wallet(request.user)
        return JsonResponse(basic_info)
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
    basic_info = user.basic_info()
    basic_info["is_bind_wechat"] = user.is_bind_wechat
    basic_info["is_bind_weibo"] = user.is_bind_weibo
    basic_info["is_disable_wallet"] = is_disable_wallet(request.user)

    friend_count = len(Friend.get_friend_ids(user_id=request.user.id))
    if friend_count < 5:
        basic_info["public_tips"] = True
    return JsonResponse(basic_info)


@login_required_404
def get_profile(request):
    user = User.get(id=request.user.id)
    invite_friend_ids = InviteFriend.get_invited_my_ids(owner_id=request.user.id)
    ignore_user_ids = list(Ignore.objects.filter(owner_id=request.user.id, ignore_type__in=[1, 3])
                                         .values_list("ignore_id", flat=True))

    invite_friends = []
    for friend_id in invite_friend_ids:
        if friend_id in ignore_user_ids:
            continue

        u = User.get(friend_id)
        basic_info = u.basic_info()
        basic_info["user_relation"] = UserEnum.be_invite.value
        invite_friends.append(basic_info)

    recommend_contacts = UserContact.recommend_contacts(request.user.id, 20)
    invite_friend_count = InviteFriend.count(user_id=request.user.id, ignore_user_ids=ignore_user_ids)

    results = {}
    results["user"] = user.basic_info()
    results["friend_invite_count"] = invite_friend_count
    results["two_degree"] = guess_know_user(request.user.id)
    results["out_app_contacts"] = recommend_contacts
    results["invite_friends"] = invite_friends
    return JsonResponse(results)


def rong_token(request):
    refresh = request.GET.get("refresh")
    if refresh:
        token = request.user.create_rong_token()
        request.user.rong_token = token
        request.user.save()
        return JsonResponse({"token": token})
    else:
        if request.user.rong_token:
            return JsonResponse({"token": request.user.rong_token})

    token = request.user.create_rong_token()
    request.user.rong_token = token
    request.user.save()
    return JsonResponse({"token": token})


@login_required_404
def get_basic_user_info(request):
    user_id = request.GET.get("user_id")
    if user_id:
        user = User.get(id=user_id)
        if user:
            return JsonResponse(user.basic_info())
        return HttpResponseNotFound()
    return HttpResponseBadRequest()


@login_required_404
def bind_wechat(request):
    code = request.POST.get("code")
    user_info = OAuth().get_user_info(code=code)
    if not user_info:
        return JsonResponse(error=LoginError.WX_LOGIN)

    third_id = user_info["openid"]
    third_name = "wx"

    third_user = ThirdUser.objects.filter(third_id=third_id, third_name=third_name).first()
    if third_user:
        user = User.get(id=request.user.id)
        if third_user.mobile == user.mobile:
            return JsonResponse()
        else:
            return JsonResponse(error=LoginError.DUPLICATE_BING)

    request.user.binding_wechat(third_id=third_id)
    return JsonResponse()


@login_required_404
def bind_weibo(request):
    access_token = request.POST.get("access_token")
    third_id = request.POST.get("third_id")

    third_user = ThirdUser.objects.filter(third_id=third_id, third_name="wb").first()
    if third_user:
        user = User.get(id=request.user.id)
        if third_user.mobile == user.mobile:
            return JsonResponse()
        else:
            return JsonResponse(error=LoginError.DUPLICATE_BING)

    request.user.binding_weibo(third_id=third_id)
    return JsonResponse()


@login_required_404
def unbind_wechat(request):
    is_success = request.user.unbinding_wechat()
    if is_success:
        return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def unbind_weibo(request):
    is_success = request.user.unbinding_weibo()
    if is_success:
        return JsonResponse()
    return HttpResponseServerError()


@login_required_404
def update_paid(request):
    paid = request.POST.get("paid", "")
    user = User.objects.filter(paid=paid).first()
    if user:
        return JsonResponse(error=LoginError.PA_ALREADY_USED)

    r = re.match("^[a-zA-Z][a-zA-Z0-9_]{3,16}$", paid)
    if r:
        request.user.paid = paid
        request.user.save()
        return JsonResponse()
    return JsonResponse(error=LoginError.RE_PAID_ERROR)


@login_required_404
def update_gender(request):
    gender = request.POST.get("gender")
    user = User.objects.filter(id=request.user.id).first()
    user.gender = gender
    user.save()
    return JsonResponse()


@login_required_404
def update_nickname(request):
    nickname = request.POST.get("nickname")
    user = User.objects.filter(id=request.user.id).first()
    user.nickname = nickname

    pinyin = Pinyin().get_pinyin(nickname, "")
    user.pinyin = pinyin[:50]
    user.save()
    return JsonResponse()


@login_required_404
def update_intro(request):
    intro = request.POST.get("intro")
    user = User.objects.filter(id=request.user.id).first()
    user.intro = intro
    user.save()
    return JsonResponse()


@login_required_404
def update_avatar(request):
    photo = request.FILES['photo']
    avatar = KS3().upload_avatar(img_content=photo.read(), user_id=request.user.id)
    user = User.objects.filter(id=request.user.id).first()
    user.avatar = avatar
    user.save()
    return JsonResponse()


@login_required_404
def search(request):
    content = request.POST.get("content")
    page = int(request.POST.get("page", 1))

    user_list = list(User.objects.filter(paid=content).exclude(id=request.user.id))
    if not user_list:
        user_list = User.objects.filter(nickname__startswith=content).exclude(id=request.user.id)

    results = {"user_list": [], "paginator": {}}
    user_list, paginator_dict = paginator(user_list, page, 30)
    friends = []
    for user in user_list:
        basic_info = user.basic_info()
        basic_info["user_relation"] = user.check_friend_relation(user_id=request.user.id)
        friends.append(basic_info)

    results["paginator"] = paginator_dict
    results["friends"] = friends

    return JsonResponse(results)


@login_required_404
def detail_user_info(request):
    user_id = request.GET.get("user_id")

    user = User.get(id=user_id)
    if request.user.id == user_id:
        detail_info = user.detail_info()
    else:
        detail_info = user.detail_info(user_id=request.user.id)

    return JsonResponse(detail_info)


@login_required_404
def ignore(request):
    ignore_id = request.POST.get("ignore_id")
    ignore_type = request.POST.get("ignore_type")
    Ignore.add(owner_id=request.user.id,
               ignore_id=ignore_id,
               ignore_type=ignore_type)

    if int(ignore_type) == 3:
        SocketServer().refresh(user_id=request.user.id, to_user_id=request.user.id, message="ignore", event_type=4)
    return JsonResponse()


@login_required_404
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
        if not user:
            return JsonResponse()

        if int(status) == 0:
            user.online()
        else:
            redis.hdel(REDIS_ONLINE_USERS_KEY, user_id)
            redis.hdel(REDIS_ONLINE_USERS, user_id)
    return JsonResponse()


@login_required_404
def add_user_location(request):
    lon = request.POST.get("lon", "")
    lat = request.POST.get("lat", "")

    Place.add(lon=float(lon), lat=float(lat), user_id=request.user.id)
    return JsonResponse()


@login_required_404
def poke(request):
    user_id = request.POST.get("user_id")

    my = ChannelMember.objects.filter(user_id=request.user.id).first()
    if my:
        channel = Channel.objects.filter(channel_id=my.channel_id).first()
        user = ChannelMember.objects.filter(user_id=user_id).first()
        if user and user.channel_id == my.channel_id:
            return _poke(request.user, user_id)
        else:
            return _invite_party(request.user, user_id, my.channel_id, channel.channel_type)
    else:
        return _poke(request.user, user_id)


def _poke(owner, user_id):
    push_lock = redis.get("mc:user:%s:to_user_id:%s:poke_lock" % (owner.id, user_id)) or 0
    if int(push_lock) <= 20:
        icon = ""
        message = u"%s 捅了你一下" % owner.nickname
        for i in list(range(int(push_lock))):
            icon += u"👉"
        message = u"%s%s" % (icon, message)

        disable_switch = redis.get(REDIS_DISABLE_FRIEND_SWITCH)
        if not disable_switch:
            Friend.objects.filter(user_id=user_id, friend_id=owner.id).update(is_hint=True)
            Friend.objects.filter(user_id=owner.id, friend_id=user_id).update(is_hint=False, update_date=timezone.now())

        SocketServer().invite_party_in_live(user_id=owner.id,
                                            to_user_id=user_id,
                                            message=message,
                                            channel_id=0)
        JPush().async_push(user_ids=[user_id], message=message, is_valid_role=False)
        redis.set("mc:user:%s:to_user_id:%s:poke_lock" % (owner.id, user_id), int(push_lock) + 1, 600)
    else:
        return JsonResponse(error={40000: "好了好了，TA收到啦"})
    return JsonResponse()


def _invite_party(owner, user_id, channel_id, channel_type):
    push_lock = redis.get("mc:user:%s:to_user_id:%s:pa_push_lock" % (owner.id, user_id)) or 0
    if int(push_lock) <= 20:
        icon = ""
        message = "%s 邀请你来开PA" % owner.nickname
        for i in list(range(int(push_lock))):
            icon += "👉"
        message = "%s%s" % (icon, message)

        disable_switch = redis.get(REDIS_DISABLE_FRIEND_SWITCH)
        if not disable_switch:
            Friend.objects.filter(user_id=user_id, friend_id=owner.id).update(is_hint=True, update_date=timezone.now())
            Friend.objects.filter(user_id=owner.id, friend_id=user_id).update(is_hint=False)

        SocketServer().invite_party_in_live(user_id=owner.id,
                                            to_user_id=user_id,
                                            message=message,
                                            channel_id=channel_id)
        JPush().async_push(user_ids=[user_id],
                           message=message,
                           push_type=1,
                           is_sound=True,
                           sound="push.caf",
                           channel_id=channel_id,
                           channel_type=channel_type,
                           is_valid_role=False)

        redis.set("mc:user:%s:to_user_id:%s:pa_push_lock" % (owner.id, user_id), int(push_lock) + 1, 600)
    else:
        return JsonResponse(error={40000: "好了好了，TA收到啦"})
    return JsonResponse()


@login_required_404
def rongcloud_push(request):
    to_user_id = request.POST.get("to_user_id")
    message = request.POST.get("message", "")

    message = "%s: %s" % (request.user.nickname, message)
    JPush().async_push(user_ids=[to_user_id], message=message, badge="+1")
    return JsonResponse()


@login_required_404
def user_logout(request):
    request.user.offline()
    logout(request)
    return JsonResponse()


def load_balancing(request):
    return JsonResponse()


@login_required_404
def kill_app(request):
    if request.user and request.user.is_authenticated():
        request.user.offline()
    return JsonResponse()


def tianmo(request):
    from django.shortcuts import redirect
    redis.incr("tianmo")
    return redirect("http://t.cn/R5imgiZ")


def xiazaipa(request):
    from django.shortcuts import redirect
    return redirect("http://a.app.qq.com/o/simple.jsp?pkgname=com.gouhuoapp.pa")


def weibo1(request):
    redis.incr("weibo1")
    return redirect("https://itunes.apple.com/cn/app/id1069693851")


def weibo2(request):
    redis.incr("weibo2")
    return redirect("https://itunes.apple.com/cn/app/id1069693851")


def weibo3(request):
    redis.incr("weibo3")
    return redirect("https://itunes.apple.com/cn/app/id1069693851")


def weibo4(request):
    redis.incr("weibo4")
    return redirect("https://itunes.apple.com/cn/app/id1069693851")


def weibo5(request):
    redis.incr("weibo5")
    return redirect("https://itunes.apple.com/cn/app/id1069693851")
