from django.views.decorators.http import require_http_methods

from corelib.http import JsonResponse
from corelib.decorators import login_required_404

from user.models import FeedBack


def add_feedback(request):
    metrics = request.POST.get("metrics")
    grade = request.POST.get("grade")

    FeedBack.objects.create(user_id=request.user.id, content=content, grade=grade)
    return JsonResponse()
