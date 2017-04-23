from django.shortcuts import render


def wechat(request):
    return render(request, 'invite/index.html', {})
