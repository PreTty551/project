from django.shortcuts import render

from ida.models import duty_party_time


def duty_live_party_time(request):
    user_ids = request.GET.get("user_ids", "")
    start_date = request.GET.get("start_date")
    days = request.GET.get("days")

    user_ids = user_ids.split("\n")
    print(user_ids)
    print("start_date",start_date)
    results = duty_party_time(user_ids=user_ids, start_date=start_date, days=days)
    print(results)
    return render(request, 'ida/live_party_time.html', {'results': results})
