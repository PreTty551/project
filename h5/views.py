from django.shortcuts import render


def main(request, user_id):
    return render(request, 'h5/main.html', {'user_id': user_id})
