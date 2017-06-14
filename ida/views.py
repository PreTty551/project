from django.shortcuts import render
from django.http import HttpResponse

from corelib.redis import redis
from ida.models import duty_party_time, user_amount, user_amount_detail
from user.models import User
import datetime

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

    data = {
        'weibo1': weibo1,
        'weibo2': weibo2,
        'weibo3': weibo3,
        'weibo4': weibo4,
        'weibo5': weibo5,
    }

    return render(request, 'ida/weibo.html', data)


def get_register_user(request):
    start = request.GET.get("start", "")
    end = request.GET.get("end", "")

    if not start:
        return HttpResponse("error")

    if end:
        user_count = User.objects.filter(date_joined__gte=start, date_joined__lte=end).count()
    else:
        user_count = User.objects.filter(date_joined__gte=start).count()
    return render(request, 'ida/register.html', {"user_count": user_count})


def get_user_amount(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get('end_date')
    if(start_date and end_date):
        date = datetime.datetime.strptime(start_date, "%Y-%m-%d %X")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d %X")
    else:
        date = datetime.datetime.now()
        end = datetime.datetime.now()

    result = []
    if request.method == 'GET':
        result = user_amount(start_date=date, end_date=end)
        if(result):
            date = datetime.datetime.strftime(date, "%Y-%m-%d %X")
            end = datetime.datetime.strftime(end, "%Y-%m-%d %X")
        if(len(result) > 0):
            amounts = result[-1]
            return render(request, 'ida/amount.html', {'result':result, 'amounts':amounts, 'date':date, 'end':end})
        else:
            return render(request, 'ida/amount.html', {'result':result})


def get_user_amount_detail(request):
    result = []
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if(start_date and end_date):
            date = datetime.datetime.strptime(start_date, "%Y-%m-%d %X")
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d %X")
        else:
            date = datetime.datetime.now()
            end = datetime.datetime.now()

        result = user_amount_detail(start_date=date, end_date=end)
        if(len(result) > 0):
            amounts = result[-1]
            print(amounts)
            return render(request, 'ida/amount_detail.html', {'result':result[0:-1], 'amounts':amounts})
        else:
            return render(request, 'ida/amount_detail.html', {'result':result})
