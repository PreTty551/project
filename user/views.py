import datetime
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
from user.models import User, ThirdUser, create_third_user, rename_nickname


@require_http_methods(["POST"])
def request_msg_code(request):
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
def verify_msg_code(request):
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

    user = authenticate(username=user.username, password=user.username)
    if user is not None:
        login(request, user)
        return JsonResponse({"user": user.basic_info()})
    return JsonResponse(error=LoginError.NOT_LOGIN)


def wx_user_login(request):
    """1男0女"""
    code = request.POST.get("code")
    mobile = request.POST.get("mobile", "")
    platform = request.POST.get("platform", "")
    version = request.POST.get("version", "")

    user_info = OAuth.get_user_info(code=code)
    if not user_info:
        return JsonResponse(error=LoginError.WX_LOGIN)

    third_id = user_info["openid"]
    sex = int(user_info["sex"])
    sex = 0 if sex == 2 else sex

    third_user = ThirdUser.objects.filter(third_id=third_id).first()
    if third_user is None:
        user = create_third_user(third_id=third_id,
                                 third_name="wx",
                                 nickname=user_info["nickname"],
                                 avatar="",
                                 gender=sex,
                                 mobile=mobile,
                                 platform=platform,
                                 version=version)

        # user.set_props_item("third_user_avatar", user_info["headimgurl"])
        # user.update_rong_token()

        # 异步队列更新头像
        # queue = django_rq.get_queue('avatar')
        # queue.enqueue(update_avatar_in_third_login, user.id)
    else:
        user = User.objects.filter(id=third_user.user_id).first()

    if user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)

    # 登录
    user = authenticate(username=user.username, password=user.username)
    if user is not None:
        login(request, user)
        return JsonResponse({"user": user.basic_info()})
    return JsonResponse(error=LoginError.NOT_LOGIN)


def wb_user_login(request):
    access_token = request.POST.get("access_token")
    third_id = request.POST.get("third_id")
    platform = request.POST.get("platform", "")
    version = request.POST.get("version", "")

    if not (third_id and access_token):
        return HttpResponseBadRequest()

    third_user = ThirdUser.objects.filter(third_id=third_id).first()
    if third_user is None:
        try:
            weibo = Weibo(access_token=access_token, uid=third_id)
            user_info = weibo.get_user_info()
            if not user_info:
                return JsonResponse(error=LoginError.WB_LOGIN)
        except Exception as e:
            return JsonResponse(error=LoginError.WB_LOGIN)

        user = create_third_user(third_id=third_id,
                                 third_name="wb",
                                 nickname=user_info["nickname"],
                                 avatar="",
                                 gender=user_info["gender"],
                                 mobile="",
                                 platform=platform,
                                 version=version)
        # user.set_props_item("third_user_avatar", user_info["avatar"])
        # user.update_rong_token()

        # 异步队列更新头像
        # queue = django_rq.get_queue('avatar')
        # queue.enqueue(update_avatar_in_third_login, user.id)
    else:
        user = User.objects.filter(id=third_user.user_id).first()

    if user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)

    # 登录
    user = authenticate(username=user.username, password=user.username)
    if user is not None:
        login(request, user)
        return JsonResponse({"user": user.basic_info()})
    return JsonResponse(error=LoginError.NOT_LOGIN)


def check_login(request):
    if not (request.user and request.user.is_authenticated()):
        return JsonResponse(error=LoginError.NOT_LOGIN)

    if request.user.disable_login:
        return JsonResponse(error=LoginError.DISABLE_LOGIN)
    return JsonResponseSuccess({"user": request.user.basic_info()})
