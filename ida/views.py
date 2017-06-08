from django.shortcuts import render
from django.http import HttpResponse

from corelib.redis import redis
from ida.models import duty_party_time
from user.models import User


def duty_live_party_time(request):
    user_ids = request.GET.get("user_ids", "")
    start_date = request.GET.get("start_date")
    days = request.GET.get("days")

    user_ids = user_ids.split("\n")
    results = duty_party_time(user_ids=user_ids, start_date=start_date, days=days)
    return render(request, 'ida/live_party_time.html', {'results': results})


def tick(request):
    from user.models import fuck_you
    user_id = request.POST.get("user_id", "")

    if request.method == "POST":
        fuck_you(user_id)
    return render(request, 'ida/tick.html')


def weibo(request):
    weibo1 = redis.get("weibo1")
    weibo2 = redis.get("weibo2")
    weibo3 = redis.get("weibo3")
    weibo4 = redis.get("weibo4")
    weibo5 = redis.get("weibo5")
    fir = redis.get("firxiazai")

    data = {
        'weibo1': weibo1,
        'weibo2': weibo2,
        'weibo3': weibo3,
        'weibo4': weibo4,
        'weibo5': weibo5,
        'firxiazai': fir,
    }

    return render(request, 'ida/weibo.html', data)


def get_register_user(request):
    start = request.POST.get("start", "")
    end = request.POST.get("end", "")

    user_count = 0
    if request.method == "POST":
        if end:
            user_count = User.objects.filter(date_joined__gte=start, date_joined__lte=end, platform=1).count()
        else:
            user_count = User.objects.filter(date_joined__gte=start, platform=1).count()
    return render(request, 'ida/register.html', {"user_count": user_count})
