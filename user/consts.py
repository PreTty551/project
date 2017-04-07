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

# memcache keys
MC_USER_KEY = "user:%s"

# 忽略类型
