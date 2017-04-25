# -*- coding: utf-8 -*-

from django.conf.urls import url

from live import views

urlpatterns = [
    url(r'^livemedia/home_list/refresh/$', views.refresh_home_list, name='refresh_home_list'),
    url(r'^livemedia/home_list/$', views.home_list, name='home_list'),
    url(r'^livemedia/list/$', views.livemedia_list, name='livemedia_list'),
    url(r'^livemedia/list/refresh/$', views.refresh_list, name='refresh_list'),
    url(r'^livemedia/channel/near/list/$', views.near_channel_list, name='near_channel_list'),
    url(r'^livemedia/channel/private/list/$', views.private_channel_list, name='private_channel_list'),
    url(r'^livemedia/channel/create/$', views.create_channel, name='create_channel'),
    url(r'^livemedia/channel/join/$', views.join_channel, name='join_channel'),
    url(r'^livemedia/channel/quit/$', views.quit_channel, name='quit_channel'),
    url(r'^livemedia/channel/delete/$', views.delete_channel, name='delete_channel'),
    url(r'^livemedia/channel/lock/$', views.lock_channel, name='lock_channel'),
    url(r'^livemedia/channel/unlock/$', views.unlock_channel, name='unlock_channel'),
    url(r'^agora/signaling_key/$', views.signaling_key, name='signaling_key'),
    url(r'^agora/user_online_callback/$', views.user_online_callback, name='user_online_callback'),
    url(r'^livemedia/guess_word/$', views.guess_word, name='guess_word'),
    url(r'^livemedia/close_guess_word/$', views.close_guess_word, name='close_guess_word'),
    url(r'^livemedia/channel/invite/$', views.invite_channel, name='invite_channel'),
    url(r'^livemedia/dirty_game/$', views.dirty_game_question, name='dirty_game_question'),
]
