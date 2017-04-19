from django.shortcuts import render


def main(request):
    return render(request, 'h5/main.html', {})
