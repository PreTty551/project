from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user/login/sms_code/request/$', views.request_msg_code, name='request_msg_code'),
    url(r'^user/login/sms_code/verify/$', views.verify_msg_code, name='verify_msg_code'),
    url(r'^user/register/$', views.register, name='register'),
    url(r'^user/login/weibo/$', views.wb_user_login, name='wb_user_login'),
    url(r'^user/login/wechat/$', views.wx_user_login, name='wx_user_login'),
    url(r'^user/check_login/$', views.check_login, name='check_login'),
]
