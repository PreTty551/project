# -*- coding: utf-8 -*-

from django.conf.urls import url

from ida import views

urlpatterns = [
    url(r'^duty/live_time/$', views.duty_live_party_time, name='duty_live_party_time'),

]
