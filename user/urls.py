from django.conf.urls import url
from user import views

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
    url(r'^user/detail_info/$', views.detail_user_info, name='detail_user_info'),
    url(r'^user/profile/$', views.get_profile, name='get_profile'),
    url(r'^user/paid/update/$', views.update_paid, name='update_paid'),
    url(r'^user/gender/update/$', views.update_gender, name='update_gender'),
    url(r'^user/nickname/update/$', views.update_nickname, name='update_nickname'),
    url(r'^user/intro/update/$', views.update_intro, name='update_intro'),
    url(r'^user/avatar/update/$', views.update_avatar, name='update_avatar'),

    url(r'^user/contact/$', views.get_contacts, name='get_contacts'),
    url(r'^user/contact/in_app/$', views.get_contacts_in_app, name='get_contacts_in_app'),
    url(r'^user/contact/out_app/$', views.get_contacts_out_app, name='get_contacts_out_app'),
    url(r'^user/contact/add/$', views.add_user_contact, name='add_user_contact'),
    url(r'^user/contact/update/$', views.update_user_contact, name='update_user_contact'),
    url(r'^user/contact/list/$', views.get_contact_list, name='get_contact_list'),
    url(r'^user/contact/common_friend/$', views.common_contact, name='common_contact'),

    url(r'^user/friend/$', views.get_friends, name='get_friends'),
    url(r'^user/friend/invite/$', views.invite_friend, name='invite_friend'),
    url(r'^user/friend/agree/$', views.agree_friend, name='agree_friend'),
    url(r'^user/friend/delete/$', views.delete_friend, name='delete_friend'),
    url(r'^user/friend/invisible/$', views.update_invisible, name='update_invisible'),
    url(r'^user/friend/push/$', views.update_push, name='update_push'),
    url(r'^user/friend/pinyin/$', views.get_friends_order_by_pinyin, name='get_friends_order_by_pinyin'),
    url(r'^user/friend/memo/update/$', views.update_user_memo, name='update_user_memo'),
    url(r'^user/friend/whos/$', views.who_is_friends, name='who_is_friends'),
    url(r'^user/unagree_count/$', views.unagree_friend_count, name='unagree_friend_count'),

    url(r'^user/ignore/$', views.ignore, name='ignore'),
    url(r'^user/rong_token/$', views.rong_token, name='rong_token'),
    url(r'^user/search/$', views.search, name='search'),
    url(r'^user/invite_party/$', views.invite_party, name='invite_party'),
    url(r'^user/party_push/$', views.party_push, name='party_push'),

    url(r'^user/quit_app/$', views.quit_app, name='quit_app'),
    url(r'^user/online_and_offine/callback/$', views.user_online_and_offine_callback, name='online_and_offine'),

    url(r'^user/bingd/wx/$', views.binding_wechat, name='binding_wechat'),
    url(r'^user/bingd/wb/$', views.binding_weibo, name='binding_weibo'),

    url(r'^user/fuck_you/$', views.fuck_you, name='fuck_you'),
    url(r'^user/location/add/$', views.add_user_location, name='add_user_location'),


]
