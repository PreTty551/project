from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^user/login/sms_code/request/$', views.request_sms_code, name='request_sms_code'),
    url(r'^user/login/sms_code/verify/$', views.verify_sms_code, name='verify_sms_code'),
    url(r'^user/register/$', views.register, name='register'),
    url(r'^user/login/weibo/$', views.wb_user_login, name='wb_user_login'),
    url(r'^user/login/wechat/$', views.wx_user_login, name='wx_user_login'),
    url(r'^user/check_login/$', views.check_login, name='check_login'),
    url(r'^user/third_login/sms_code/request/$', views.third_request_sms_code, name='third_request_sms_code'),
    url(r'^user/third_login/sms_code/verify/$', views.third_verify_sms_code, name='third_verify_sms_code')

]
