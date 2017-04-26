from .contact import UserContact
from .ignore import Ignore
from .friend import Friend, InviteFriend
from .user import User
from user.consts import UserEnum


def two_degree_relation(user_id):
    friend_ids = list(Friend.objects.filter(user_id=user_id)
                                    .values_list("friend_id", flat=True))
    second_friend_list = list(Friend.objects.filter(user_id__in=friend_ids)
                                            .exclude(friend_id=user_id)
                                            .exclude(friend_id__in=friend_ids)
                                            .values_list("user_id", "friend_id"))

    obj = []
    for second_friend in second_friend_list:
        obj.append((second_friend[0], second_friend[1]))

    _dict = {}
    for uid, fid in obj:
        _ = _dict.setdefault(fid, [])
        _.append(uid)
    result = []

    users = []
    for user_id, mutual_friend_ids in _dict.items():
        if len(mutual_friend_ids) >= 2:
            users.append((user_id, len(mutual_friend_ids)))

    sort_users = sorted(users, key=lambda item: item[1], reverse=True)
    return sort_users


def guess_know_user(user_id):
    all_mobile_list = list(UserContact.objects.filter(user_id=user_id).values_list("mobile", flat=True))
    friend_ids = Friend.get_friend_ids(user_id=user_id)
    invited_my_ids = InviteFriend.get_invited_my_ids(owner_id=user_id)
    my_invited_ids = InviteFriend.get_my_invited_ids(owner_id=user_id)
    ignore_ids = list(Ignore.objects.filter(owner_id=user_id, ignore_type=1).values_list("ignore_id", flat=True))
    user_ids = list(User.objects.filter(mobile__in=all_mobile_list)
                                .exclude(id__in=friend_ids)
                                .exclude(id__in=invited_my_ids)
                                .exclude(id__in=my_invited_ids)
                                .exclude(id__in=ignore_ids)
                                .values_list("id", flat=True))

    if user_id in user_ids:
        user_ids.remove(user_id)

    results = []
    users = [User.get(id=user_id) for user_id in user_ids[:10]]
    for user in users:
        basic_info = user.basic_info()
        basic_info["reason"] = "通讯录好友"
        basic_info["user_relation"] = UserEnum.nothing.value
        results.append(basic_info)

    two_degrees = two_degree_relation(user_id=user_id)[:10]
    for user_id, common_friend_count in two_degrees:
        user = User.get(id=user_id)
        basic_info = user.basic_info()
        basic_info["reason"] = "你们有%s个共同好友" % common_friend_count
        basic_info["user_relation"] = UserEnum.nothing.value
        results.append(basic_info)

    return results
