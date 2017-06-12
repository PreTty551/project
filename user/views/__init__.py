from .contact import get_contacts, add_user_contact, update_user_contact, \
                     get_contact_list, common_contact
from .friend import invite_friend, agree_friend, get_friends_order_by_pinyin, update_user_memo, \
                    who_is_friends, delete_friend, update_invisible, update_push, unagree_friend_count, friend_relation
from .user import request_sms_code, request_voice_code, verify_sms_code, register, wx_user_login, wb_user_login, \
                  third_request_sms_code, third_verify_sms_code, check_login, get_profile, rong_token, \
                  get_basic_user_info, detail_user_info, search, update_paid, update_gender, \
                  update_nickname, quit_app, user_online_and_offine_callback, update_intro, bind_wechat, bind_weibo, \
                  update_avatar, add_user_location, unbind_wechat, unbind_weibo, ignore, poke, rongcloud_push, \
                  user_logout, load_balancing, tianmo, kill_app, third_request_voice_code, xiazaipa, weibo1, weibo2, \
                  weibo3, weibo4, weibo5, firxiazai, report
from .feedback import add_feedback, check_ios_version, say_ios
