import random

from django.test import TestCase

from user.models import User, Firend, two_degree_relation


class UsersTestCase(TestCase):
    def setUp(self):
        pass

    def setDown(self):
        pass

    def _init_data(self):
        mobile = random.randint(13000000000, 14000000000)
        names = ["ida", "dark", "qingfeng", "mengwei", "ss", "gd", "jh"]
        user_list = []
        for name in names:
            _ = {"nickname": name, "mobile": mobile}
            user_list.append(_)

        for user in user_list:
            User.objects.add_user(nickname=user["nickname"], mobile=user["mobile"])

        for i in range(2, 5):
            Firend.invite(user_id=1, firend_id=i)
            Firend.agree(user_id=1, firend_id=i)

        Firend.invite(user_id=5, firend_id=2)
        Firend.agree(user_id=5, firend_id=2)

        Firend.invite(user_id=6, firend_id=3)
        Firend.agree(user_id=6, firend_id=3)

        Firend.invite(user_id=7, firend_id=1)
        Firend.agree(user_id=7, firend_id=1)

        f = Firend.objects.filter(user_id=7).first()
        Firend.invite(user_id=7, firend_id=5)
        Firend.agree(user_id=7, firend_id=5)
        Firend.invite(user_id=7, firend_id=6)
        Firend.agree(user_id=7, firend_id=6)

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

        degree_user_list[0]["id"] == 2
        degree_user_list[0]["mutual_firend"] == ['ida', 'ss']

        degree_user_list[0]["id"] == 3
        degree_user_list[0]["mutual_firend"] == ['ida', 'gd']

        degree_user_list[0]["id"] == 4
        degree_user_list[0]["mutual_firend"] == ['ida']
