import random

from django.test import TestCase, TransactionTestCase

from user.models import User, Friend, InviteFriend, two_degree_relation, BanUser                    


class UsersTestCase(TransactionTestCase):
    def setUp(self):
        pass

    def setDown(self):
        pass

    def _init_data(self):
        names = ["ida", "dark", "qingfeng", "mengwei", "ss", "gd", "jh"]
        user_list = []
        for name in names:
            mobile = random.randint(13000000000, 14000000000)
            _ = {"nickname": name, "mobile": mobile}
            user_list.append(_)

        for user in user_list:
            User.objects.add_user(nickname=user["nickname"], mobile=user["mobile"])

        for i in range(2, 5):
            InviteFriend.add(user_id=1, invited_id=i)
            InviteFriend.agree(user_id=1, invited_id=i)

        InviteFriend.add(user_id=5, invited_id=2)
        InviteFriend.agree(user_id=5, invited_id=2)

        InviteFriend.add(user_id=6, invited_id=3)
        InviteFriend.agree(user_id=6, invited_id=3)

        InviteFriend.add(user_id=7, invited_id=1)
        InviteFriend.agree(user_id=7, invited_id=1)

        f = Friend.objects.filter(user_id=7).first()
        InviteFriend.add(user_id=7, invited_id=5)
        InviteFriend.agree(user_id=7, invited_id=5)
        InviteFriend.add(user_id=7, invited_id=6)
        InviteFriend.agree(user_id=7, invited_id=6)


    def test_degree_friend(self):
        """
        7: [1, 5, 6]
        1: [2, 3, 4]
        5: [2]
        6: [3]
        """
        self._init_data()
        assert User.objects.all().count() == 7

        degree_user_list = two_degree_relation(7)

        assert degree_user_list[0]["id"] == 2
        assert degree_user_list[0]["mutual_friend"] == ['ida', 'ss']

        assert degree_user_list[1]["id"] == 3
        assert degree_user_list[1]["mutual_friend"] == ['ida', 'gd']

        assert degree_user_list[2]["id"] == 4
        assert degree_user_list[2]["mutual_friend"] == ['ida']

    def test_disable_login(self):
        User.objects.add_user(nickname="aaa",mobile="18334793471")
        user = User.get(id=1)
        User.objects.add_user(nickname="bbb",mobile="18334793472")
        BanUser.add(user_id=2,second=86400)
        banuser = BanUser.get(id=1)
        assert user.disable_login == False
        user = User.get(id=)
        assert user.disable_login == True