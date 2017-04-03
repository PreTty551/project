from enum import Enum

Gender = Enum("Gender", ("male", "female"))
FirendEnum = Enum("FirendEnum", ("invite", "be_invite", "firend", "ignore"))

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
