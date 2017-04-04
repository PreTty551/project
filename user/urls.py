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
    url(r'^user/third_login/sms_code/verify/$', views.third_verify_sms_code, name='third_verify_sms_code'),
    url(r'^user/basic_info/$', views.get_basic_user_info, name='basic_user_info'),
    url(r'^user/contact/$', views.get_contacts, name='get_contacts'),
    url(r'^user/contact/in_app/$', views.get_contacts_in_app, name='get_contacts_in_app'),
    url(r'^user/contact/out_app/$', views.get_contacts_out_app, name='get_contacts_out_app'),
    url(r'^user/contact/add/$', views.add_user_contact, name='add_user_contact'),
    url(r'^user/contact/update/$', views.update_user_contact, name='update_user_contact'),
]
