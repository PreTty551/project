from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^gift/list/$', views.gift_list, name='gift_list'),
    url(r'^gift/send/$', views.gift_transfer, name='send_gift'),
]
