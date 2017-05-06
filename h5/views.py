from django.shortcuts import render


def main(request):
    return render(request, 'h5/main.html', {})


def clause(request):
    static_url = 'http://7xp90p.com2.z0.glb.qiniucdn.com'
    return render(request, 'h5/clause.html', {'static_url': static_url})
