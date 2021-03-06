from django.shortcuts import render, redirect
from django.http import HttpResponse

from user.models import User
from live.models import ChannelMember, Channel


def wechat(request, user_id):
    user = User.get(id=user_id)
    channelmember = ChannelMember.objects.filter(user_id=user_id).first()
    if channelmember:
        channel = Channel.get_channel(channelmember.channel_id)
        is_lock = channel.is_lock
        channel_id = channel.channel_id

        if is_lock:
            return redirect('invite_pa', user_id=user_id)

        return render(request, 'invite/index.html', {'user': user, 'channel': channel})
    else:
        return redirect('invite_pa', user_id=user_id)


def pa(request, user_id):
    user = User.get(id=user_id)
    channelmember = ChannelMember.objects.filter(user_id=user_id).first()
    channel = None
    if channelmember:
        channel = Channel.get_channel(channelmember.channel_id)
    return render(request, 'invite/index1.html', {'user': user, 'channel': channel})


def download(request):
    return redirect('https://itunes.apple.com/app/say-视频群聊/id1069693851')


def file_download(request):
    with open('/home/mengwei/apple-app-site-association') as f:
        c = f.read()
    response = HttpResponse(c)
    response['Content-Type'] = 'application/json'
    return response


def android_download(request):
    with open('/home/mengwei/android.apk', "rb") as f:
        c = f.read()
    response = HttpResponse(c)
    response['Content-Length'] = len(c)
    response['Content-Type'] = 'application/vnd.android.package-archive'
    return response


def home(request):
    return render(request, 'invite/house_index.html')
