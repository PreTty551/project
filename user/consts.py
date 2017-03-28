from enum import Enum

Gender = Enum("Gender", ("male", "female"))

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


# 好友
F_INVITE = 1
F_BE_INVITE = 2
F_FIREND = 3
F_IGNORE = 4
