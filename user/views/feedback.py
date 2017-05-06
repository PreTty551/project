from django.views.decorators.http import require_http_methods
from django.http import HttpResponseNotFound, JsonResponse as JR

from corelib.http import JsonResponse
from corelib.decorators import login_required_404

from user.models import FeedBack


def add_feedback(request):
    metrics = request.POST.get("metrics")
    grade = request.POST.get("grade")

    FeedBack.objects.create(user_id=request.user.id, content=metrics, grade=grade)
    return JsonResponse()


def check_ios_version(request):
    version = request.POST.get("version", 0)
    if int(version) < 14:
        content = {
            "version": int(version),
            "title": u"更新提醒",
            "content": u"PA更新了，立即更新体验Pa的新功能吧！",
            "is_force_update": False,
            "download_url": "https://itunes.apple.com/cn/app/id1069693851"
        }
        return JsonResponse(content)
    return HttpResponseNotFound()


def say_ios(request):
    code = 10000
    results = {
        "code_name": "v1.5.20",
        "code": code,
        "title": u"重大更新",
        "content": u"SAY更名为「开PA」，快前往应用商店下载吧！",
        "is_force_update": True,
        "download_url": "https://itunes.apple.com/cn/app/id1069693851"
    }

    return JR({'results': results, "response": {"status_code": 200}})
