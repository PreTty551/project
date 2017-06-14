# -*- coding: utf-8 -*-

from django.conf.urls import url

from ida import views

urlpatterns = [
    url(r'^duty/live_time/$', views.duty_live_party_time, name='duty_live_party_time'),
    url(r'^ida/tick/$', views.tick, name='tick'),
    url(r'^ida/weibo/$', views.weibo, name='weibo'),
    url(r'^ida/register/search/$', views.get_register_user, name='get_register_user'),
    url(r'^ida/user_amount/$', views.get_user_amount, name='get_user_amount'),
    url(r'^ida/user_amount_detail/$', views.get_user_amount_detail, name='get_user_amount_detail'),
]
