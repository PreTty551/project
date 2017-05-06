"""ida_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url, include
from django.contrib import admin

from h5 import views
from invite.views import file_download

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('user.urls')),
    url(r'', include('live.urls')),
    url(r'', include('gift.urls')),
    url(r'', include('wallet.urls')),
    url(r'^invite/', include('invite.urls')),
    url(r'^h5/$', views.main),
    url(r'^apple-app-site-association$', file_download),
    url(r'^clause/$', views.clause),
]

urlpatterns += staticfiles_urlpatterns()
