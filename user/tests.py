import random

from django.test import TestCase, TransactionTestCase

from user.models import User, Firend, InviteFirend, two_degree_relation


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
            InviteFirend.add(user_id=1, invited_id=i)
            InviteFirend.agree(user_id=1, invited_id=i)

        InviteFirend.add(user_id=5, invited_id=2)
        InviteFirend.agree(user_id=5, invited_id=2)

        InviteFirend.add(user_id=6, invited_id=3)
        InviteFirend.agree(user_id=6, invited_id=3)

        InviteFirend.add(user_id=7, invited_id=1)
        InviteFirend.agree(user_id=7, invited_id=1)

        f = Firend.objects.filter(user_id=7).first()
        InviteFirend.add(user_id=7, invited_id=5)
        InviteFirend.agree(user_id=7, invited_id=5)
        InviteFirend.add(user_id=7, invited_id=6)
        InviteFirend.agree(user_id=7, invited_id=6)

    def test_degree_firend(self):
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
        assert degree_user_list[0]["mutual_firend"] == ['ida', 'ss']

        assert degree_user_list[1]["id"] == 3
        assert degree_user_list[1]["mutual_firend"] == ['ida', 'gd']

        assert degree_user_list[2]["id"] == 4
        assert degree_user_list[2]["mutual_firend"] == ['ida']
