import json
import factory
import geojson
from authorization.factories import UserFactory
from .models import Category, Point, Game, Round


def generate_random_point():
    return json.dumps(geojson.utils.generate_random("Point"))


class CategoryFactory(factory.django.DjangoModelFactory):
    codename = factory.Sequence(lambda n: 'codename_{}'.format(n))
    name = factory.Sequence(lambda n: 'name_{}'.format(n))
    description = factory.Sequence(lambda n: 'description_{}'.format(n))
    rounds_count = 5

    class Meta:
        model = Category


class PointFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    point = factory.LazyFunction(generate_random_point)

    class Meta:
        model = Point


class GameFactory(factory.django.DjangoModelFactory):
    category = factory.SubFactory(CategoryFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Game


class RoundFactory(factory.django.DjangoModelFactory):
    game = factory.SubFactory(GameFactory)

    class Meta:
        model = Round



