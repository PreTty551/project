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
MC_USER_KEY = "u:%s"
MC_IS_FRIEND_KEY = "u:%s:f:%s"
MC_FRIEND_IDS_KEY = "u:%s:fs"


REDIS_MEMOS_KEY = 'u:%s:memo'
REDIS_INVISIBLE_KEY = 'u:%s:invisible'
REDIS_PUSH_KEY = 'u:%s:push'
REDIS_ONLINE_USERS_KEY = 'online:user_ids'
