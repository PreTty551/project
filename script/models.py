from django.db import models

from user.models import User, Friend, ChannelAddFriendLog

one_group_user_ids = """
170504
170325
170388
170480
170375
170352
170343
170396
170522
170326
170337
170395
170509
170539
170448
170398
170378
170648
170504
170342
"""

two = """
170418
170419
170421
170416
170420
170409
170426
170425
170430
170417
170415
170429
170427
170407
170408
170431
170442
170414
170447
170510
170568
170613
170589
170583
"""

three = """170358 170306"""


def duty_user(user_ids):
    public_party_ids = []
    friend_party_ids = []

    table_title = "日期 值班人ID 昵称 朋友总数 好友party 总数 公开party 总数"
    f = open("/home/mengwei/1", "w+")

    for user_id in user_ids:
        user = User.get(user_id)
        friend_ids = Friend.objects.filter(user_id=user_id).values_list("friend_id", falt=True)
        logs = ChannelAddFriendLog.objects.filter(user_id=user_id).values_list("friend_id", "channel_type").distinct()
        for friend_id, channel_type in logs:
            if channel_type == ChannelType.public.value:
                public_party_ids.append(friend_id)
            else:
                friend_party_ids.append(friend_id)

        logs = ChannelAddFriendLog.objects.filter(friend_id=user_id).values_list("user_id", "channel_type").distinct()
        for user_id, channel_type in logs:
            if channel_type == ChannelType.public.value:
                if user_id not in public_party_ids:
                    public_party_ids.append(user_id)
            else:
                if user_id not in friend_party_ids:
                    friend_party_ids.append(user_id)

        public_party_ids = set(friend_ids) & set(public_party_ids)
        friend_party_ids = set(friend_ids) & set(friend_party_ids)
        data = [datetiem.datetime.now(), user_id, user.nickname, len(friend_ids),
                " ".join(friend_party_ids), len(friend_party_ids),
                " ".join(public_party_ids), len(public_party_ids)]
        f.write(",".join(data))

    f.close()


def run():
    ids = one_group_user_ids.split("\n")
    duty_user(ids)
