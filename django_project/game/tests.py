import json
from unittest.mock import patch, PropertyMock
import geojson
from django.urls import reverse
from django.contrib.gis.geos import GEOSGeometry, LineString
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework_gis.serializers import GeometryField
from authorization.factories import UserFactory
from .models import Point, Game, Round
from .factories import (PointFactory, CategoryFactory, GameFactory,
                        RoundFactory)
from .serializers import CategorySerializer
from .permissions import PlayInCategoryPermission
from .views import CategoryViewSet, top_players


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

    @patch.object(Round, 'set_score')
    def test_score(self, mock_method):
        game = GameFactory()
        round_1 = RoundFactory(score=1, game=game)
        round_2 = RoundFactory(score=2, game=game)
        game.set_score()
        game.save()
        self.assertEqual(game.score, 3)


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

    def test_get_score(self):
        user_point = GEOSGeometry(json.dumps(geojson.utils.generate_random('Point')))
        random_point = PointFactory()
        _round = RoundFactory()
        ls = LineString(user_point, random_point.point, srid=4326)
        ls.transform(54009)
        distance = ls.length
        score = 5000
        if distance > 150:
            score -= distance
        score = score if score > 0 else 0
        _round.user_point = user_point
        _round.random_point = random_point
        _round.save()
        self.assertEqual(_round.score, score)



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
        self.assertEqual(response.data['category'],
                         CategorySerializer(category).data)
        self.assertEqual(response.data['random_point'],
                         GeometryField().to_representation(point.point))

    def test_next_round(self):
        category = CategoryFactory()
        point = PointFactory(category=category)
        game = GameFactory(category=category)
        url = reverse('game-next_round', kwargs={'pk': game.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RoundViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory(password='password')
        self.client.login(username=self.user.login,
                          password='password')

    def test_set_user_point(self):
        round = RoundFactory(random_point=PointFactory())
        data = {
            'user_point': geojson.utils.generate_random('Point')
        }
        url = reverse('round-set_user_point', kwargs={'pk': round.pk})
        response = self.client.patch(url, data=data, format='json')
        round.refresh_from_db(fields=['user_point', 'score'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(round.user_point,
                         GEOSGeometry(json.dumps(data['user_point'])))
        self.assertEqual(response.data['score'], round.score)
        self.assertEqual(response.data['distance_between_points'],
                         round.distance_between_points)


class CategoryViewSetTest(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory(password='password')
        self.client.login(username=self.user.login,
                          password='password')

    def test_set_like(self):
        category = CategoryFactory()
        game = GameFactory(category=category, user=self.user, is_over=True)
        url = reverse('category-set_like', kwargs={'pk': category.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, category.likes.all())


class PlayInCategoryPermissionTest(APITestCase):
    def setUp(self) -> None:
        self.category = CategoryFactory()
        self.user = UserFactory()
        self.permission = PlayInCategoryPermission()
        self.view = CategoryViewSet()
        self.request = APIRequestFactory().post('/')
        self.request.user = self.user

    def test_allow(self):
        game = GameFactory(user=self.user,
                           category=self.category,
                           is_over=True)
        self.assertTrue(self.permission.has_object_permission(self.request,
                                                              self.view,
                                                              self.category))

    def test_deny(self):
        self.assertFalse(self.permission.has_object_permission(self.request,
                                                              self.view,
                                                              self.category))


class TopPlayersViewTest(APITestCase):
    def test_top_players(self):
        request_factory = APIRequestFactory()
        url = reverse('top_players')
        request = request_factory.get(url, {'limit': 5})
        user_1 = UserFactory()
        user_2 = UserFactory()
        category = CategoryFactory(rounds_count=1)
        game_1 = GameFactory(category=category,
                             user=user_1,
                             score=1000)
        game_2 = GameFactory(category=category,
                             user=user_1,
                             score=2000)
        game_3 = GameFactory(category=category,
                             user=user_2,
                             score=3000)
        game_4 = GameFactory(category=category,
                             user=user_2,
                             score=4000)
        response = top_players(request)
        self.assertEqual(response.data[0], {'id': user_2.id,
                                            'login': user_2.login,
                                            'avg_score': (game_3.score/category.max_score + game_4.score/category.max_score)*100/2})




