from enum import Enum

Gender = Enum("Gender", ("male", "female"))
UserEnum = Enum("UserEnum", ("nothing", "contact_in_app", "contact_out_app", "invite", "be_invite", "friend", "ignore"))

# special mobile
APPSTORE_MOBILE = "12345678901"
ANDROID_MOBILE = "10987654321"
SAY_MOBILE = "10020030040"

EMOJI_LIST = [u"😀", u"😁", u"😃", u"😄", u"😇", u"😉", u"😊", u"🙂", u"😋", u"😘",
              u"😺", u"😸", u"😻", u"👍", u"👌", u"🤘", u"🕶", u"🐼", u"🐨", u"🐧",
              u"🦄", u"🐝", u"🌵", u"🍀", u"🎄", u"🌲", u"🍁", u"🌻", u"🌙", u"⭐️",
              u"✨", u"🍎", u"🍓", u"🍍", u"🍒", u"🌽", u"🍔", u"🍟", u"⚽️", u"🏀",
              u"🏈", u"🏐", u"🎱", u"🚗", u"🚕", u"🚙", u"🚀", u"🎇", u"🌠", u"🎀"]

# cache keys
MC_USER_KEY = "user:%s"
MC_IS_FRIEND_KEY = "u:%s:f:%s"
MC_FRIEND_IDS_KEY = "user:%s:fs"
MC_FRIEND_LIST = "u:%s:fl"
MC_INVITE_MY_FRIEND_IDS = "inv:my:%s:ids"
MC_MY_INVITE_FRIEND_IDS = "my:inv:%s:ids"
MC_RECOMMEND_CONTACT = "u:%s:rc"

REDIS_MEMOS_KEY = 'u:%s:f:%s:memo'
REDIS_ONLINE_USERS_KEY = 'online:user_ids'
REDIS_ONLINE_USERS = "online_user_ids"

REDIS_NO_PUSH_IDS = "u:%s:no_push"
