from unittest.mock import patch, PropertyMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from authorization.factories import UserFactory
from .models import Point, Game
from .factories import (PointFactory, CategoryFactory, GameFactory,
                        RoundFactory)


def generate_rounds_for_game(game, count):
    for i in range(count):
        RoundFactory(game=game)


class PointModelTest(APITestCase):
    def setUp(self) -> None:
        self.category = CategoryFactory()
        self.point_1 = PointFactory(category=self.category)
        self.point_2 = PointFactory(category=self.category)
        self.point_3 = PointFactory(category=self.category)

    def test_random_point(self):
        random_point = Point.objects.filter(category=self.category).random()
        self.assertEqual(random_point.category, self.category)

    def test_random_point_with_exclude(self):
        random_point = Point.objects.filter(category=self.category).\
            random(exclude_pk=[self.point_1.pk])
        self.assertEqual(random_point.category, self.category)
        self.assertNotEqual(random_point, self.point_1)


class GameModelTest(APITestCase):
    def test_round_counts(self):
        game = GameFactory()
        generate_rounds_for_game(game, count=5)
        self.assertEqual(game.round_counts, 5)

    def test_used_points_pk(self):
        game = GameFactory()
        point_1 = PointFactory()
        point_2 = PointFactory()
        round_1 = RoundFactory(game=game, random_point=point_1)
        round_2 = RoundFactory(game=game, random_point=point_2)
        points_ids = game.used_points_pk
        self.assertIn(point_1.pk, points_ids)
        self.assertIn(point_2.pk, points_ids)


class RoundModelTest(APITestCase):
    def test_set_round_num(self):
        game = GameFactory()
        generate_rounds_for_game(game, count=5)
        round = RoundFactory(game=game)
        round.set_round_num()
        self.assertEqual(round.num, 6)

    @patch.object(Game, 'used_points_pk', new_callable=PropertyMock)
    def test_set_random_point(self, mock_used_points_pk):
        category = CategoryFactory()
        point_1 = PointFactory(category=category)
        point_2 = PointFactory(category=category)
        point_3 = PointFactory(category=category)
        mock_used_points_pk.return_value = [point_1.pk, point_2.pk]
        game = GameFactory(category=category)
        round = RoundFactory(game=game)
        round.set_random_point()
        self.assertEqual(round.random_point, point_3)


class GameViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory(password='password')
        self.client.login(username=self.user.login,
                          password='password')

    def test_start_game(self):
        category = CategoryFactory()
        point = PointFactory(category=category)
        data = {
            'category': category.codename
        }
        url = reverse('game-start_game')
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print(response.data)






