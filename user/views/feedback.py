from django.views.decorators.http import require_http_methods

from corelib.http import JsonResponse
from corelib.decorators import login_required_404


def add_feedback(request):
    content = request.POST.get("content")
    FeedBack.objects.create(user_id=request.user.id, content=content)
    return JsonResponse()
