from django.shortcuts import render, redirect
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

        return render(request, 'invite/index.html', {'user': user, 'channel_id': channel_id})
    else:
        return redirect('invite_pa', user_id=user_id)

def pa(request, user_id):
    user = User.get(id=user_id)
    return render(request, 'invite/index1.html', {'user': user})

