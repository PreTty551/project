from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^wechat/$', views.wechat, name='invite_wechat'),
]
