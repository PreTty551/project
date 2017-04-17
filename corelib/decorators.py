from django.http import HttpResponseNotFound

from functools import wraps


def login_required_404(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user and not request.user.is_authenticated():
            return HttpResponseNotFound()
        return func(request, *args, **kwargs)
    return wrapper
