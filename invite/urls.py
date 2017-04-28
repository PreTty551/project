from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<user_id>\d+)/wechat/$', views.wechat, name='invite_wechat'),
    url(r'^(?P<user_id>\d+)/pa/$', views.pa, name='invite_pa'),
    url(r'^download/$', views.download, name='invite_download'),
    url(r'^home/$', views.home, name='invite_home'),
]
