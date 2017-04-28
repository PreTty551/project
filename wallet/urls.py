from django.conf.urls import url

from wallet import views

urlpatterns = [
    url(r'^wallet/$', views.wallet, name='wallet'),
    url(r'^wallet/wechat_recharge/$', views.wechat_recharge, name='wechat_recharge'),
    url(r'^wallet/wechat_recharge_callback/$', views.wechat_recharge_callback, name='wechat_recharge_callback'),
    url(r'^wallet/client_recharge_callback/$', views.client_recharge_callback, name='client_recharge_callback'),
    url(r'^wallet/withdrawal/wechat/apply/$', views.apply_withdrawal_to_wechat, name='apply_withdrawal_to_wechat'),
    url(r'^wallet/is_disable/$', views.is_disable, name='is_disable'),
    url(r'^wallet/record/list/$', views.wallet_record, name='wallet_record')
]
