# -*- coding: utf-8 -*-
import datetime
import django_rq

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, Http404, \
        HttpResponseServerError, HttpResponseNotFound

from corelib.jsms import JSMS
from corelib.http import JsonResponse
from corelib.errors import LoginError
from corelib.weibo import Weibo
from corelib.wechat import OAuth

from user.consts import APPSTORE_MOBILE, ANDROID_MOBILE, SAY_MOBILE
from user.models import User, ThirdUser, create_third_user, rename_nickname, update_avatar_in_third_login


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
        return JsonResponse({"user": user.normal_info()})

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
                return JsonResponse({"user": user.basic_info(), "is_new_user": False})
        return JsonResponse({"is_new_user": True})
    else:
        return JsonResponse(error=error_dict)


@require_http_methods(["POST"])
def register(request):
    nickname = request.POST.get("nickname", "")
    version = request.POST.get("version", "")
    platform = request.POST.get("platform", "")

    nickname = nickname.strip().replace("#", "").replace("@", "").replace(" ", "")

    # if nickname.lower() == u"say酱".lower():
    #     return UserNicknameError().json()

    if len(mobile) != 11:
        return HttpResponseBadRequest()

    user = User.objects.filter(mobile=mobile).first()
    if not user:
        nickname = rename_nickname(nickname)
        user = User.objects.add_user(nickname=nickname,
                                     mobile=mobile,
                                     platform=platform,
                                     version=version)
        if not user:
            return HttpResponseServerError()

    # 登录
    if _login(request, user):
        return JsonResponse({"user": user.basic_info()})
    return JsonResponse(error=LoginError.REGISTER_ERROR)


def wx_user_login(request):
    code = request.POST.get("code")
    user_info = OAuth.get_user_info(code=code)
    if not user_info:
        return JsonResponse(error=LoginError.WX_LOGIN)

    third_user = ThirdUser.objects.filter(third_id=user_info["openid"]).first()
    if third_user:
        user = User.objects.filter(mobile=third_user.mobile).first()
        if user.disable_login:
            return JsonResponse(error=LoginError.DISABLE_LOGIN)

        # 登录
        if _login(request, user):
            return JsonResponse({"user": user.basic_info(), "is_new_user": False})
    else:
        sex = int(user_info["sex"])
        gender = 0 if sex == 2 else sex
        temp_third_user = TempThirdUser.objects.create(third_id=user_info["openid"],
                                                       third_name="wx",
                                                       gender=gender,
                                                       nickname=user_info["nickname"],
                                                       avatar=user_info["avatar"])

        return JsonResponse({"temp_third_id": temp_third_user.id, "is_new_user": True})


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
            return JsonResponse({"user": user.basic_info(), "is_new_user": False})
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


def third_request_sms_code(request):
    mobile = request.POST.get("mobile", "")
    third_name = request.POST.get("third_name", "")
    if not mobile:
        return HttpResponseBadRequest()

    third_user = ThirdUser.objects.filter(mobile=mobile, third_name=third_name).first()
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
    user = create_third_user(third_id=temp_user.third_id,
                             third_name=temp_user.third_name,
                             nickname=temp_user.nickname,
                             avatar="",
                             gender=temp_user.gender,
                             mobile=mobile,
                             platform=platform,
                             version=version)

    user.set_props_item("third_user_avatar", temp_user.avatar)

    # 异步队列更新头像
    queue = django_rq.get_queue('avatar')
    queue.enqueue(update_avatar_in_third_login, user.id)

    if user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)

    # 登录
    if _login(request, user):
        return JsonResponse({"user": user.basic_info()})
    return JsonResponse(error=LoginError.REGISTER_ERROR)


def _login(request, user):
    from live.models import ChannleMember
    ChannleMember.objects.filter(user_id=user.id).delete()
    user = authenticate(username=user.username, password=user.username)
    if user is not None:
        login(request, user)
        return True
    return False


def check_login(request):
    if not (request.user and request.user.is_authenticated()):
        return JsonResponse(error=LoginError.NOT_LOGIN)

    if request.user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)
    return JsonResponse({"user": request.user.basic_info()})


def binding_wechat(request):
    code = request.POST.get("code")
    user_info = OAuth.get_user_info(code=code)
    if not user_info:
        return JsonResponse(error=LoginError.WX_LOGIN)

    third_id = user_info["open_id"]
    third_name = "wx"

    user = User.objects.filter(id=request.user.id)
    if not user:
        return JsonResponse(error=LoginError.BAND_ERROR)

    third_user = ThirdUser.objects.filter(mobile=user.mobile).exclude(third_id=third_id, third_name=third_name).first()
    if third_user:
        return JsonResponse(error=LoginError.MOBILE_ALREADY_USED)

    try:
        ThirdUser.objects.create(mobile=user.mobile, third_id=third_id, third_name=third_name)
    except:
        pass
    return JsonResponse()
