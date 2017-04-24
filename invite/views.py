from django.shortcuts import render
# from user.models import User


def wechat(request, user_id):
    # user = User.get(id=user_id)
    user = ""
    return render(request, 'invite/index.html', {'user_id': user_id})

def play(request, user_id):
    # user = User.get(id=user_id)
    user = ""
    return render(request, 'invite/play.html', {'user_id': user_id})
