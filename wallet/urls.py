from django.conf.urls import url

from wallet import views

urlpatterns = [
    url(r'^wallet/$', views.wallet, name='wallet'),
    url(r'^wallet/wechat_recharge/$', views.wechat_recharge, name='wechat_recharge'),
    url(r'^wallet/wechat_recharge_callback/$', views.wechat_recharge_callback, name='wechat_recharge_callback'),
    url(r'^wallet/withrawal/wechat/apply/$', views.apply_withdrawal_to_wechat, name='apply_withdrawal_to_wechat'),
]
