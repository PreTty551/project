from django.shortcuts import render
# from user.models import User


def wechat(request, user_id):
    # user = User.get(id=user_id)
    user = ""
    return render(request, 'invite/index1.html', {'user': user})
