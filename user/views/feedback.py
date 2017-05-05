from django.views.decorators.http import require_http_methods
from django.http import HttpResponseNotFound

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
    code = 1
    results = {
        "code_name": "v1.5.20",
        "code": code,
        "title": u"更新提醒",
        "content": u"SAY更新了，立即更新体验Party的新功能吧！",
        "is_force_update": False,
        "download_url": "https://itunes.apple.com/cn/app/id1069693851"
    }

    return JsonResponse({'results': results, "response": {"status_code": 200}})
