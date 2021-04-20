import random
from typing import List, Optional
from django.core.validators import MinValueValidator
from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver


class Category(models.Model):
    codename = models.CharField(max_length=20, verbose_name='Кодовое имя')
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Картинка')
    rounds_count = models.IntegerField(verbose_name='Число раундов')
    max_score = models.PositiveIntegerField(default=1, validators=[MinValueValidator(limit_value=1)])
    likes = models.ManyToManyField(to='authorization.User', related_name='liked_category')

    @property
    def points_count(self):
        return self.points.all().count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


@receiver(post_save, sender=Category)
def set_max_score(sender, instance, created, **kwargs):
    if created:
        instance.max_score = 5000 * instance.rounds_count
        instance.save()


class PointQueryset(models.QuerySet):
    def random(self, exclude_pk: Optional[List[int]]=None):

        ids = (self.exclude(pk__in=exclude_pk).values_list('id', flat=True) if exclude_pk
               else self.values_list('id', flat=True))
        random_id = random.choice(list(ids))
        return self.get(pk=random_id)


class Point(models.Model):
    point = models.PointField(verbose_name='Точка')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='points',
                                 verbose_name='Категория')

    objects = PointQueryset.as_manager()

    def __str__(self):
        return '{} {}'.format(self.category.name, self.pk)

    class Meta:
        verbose_name = 'Точка'
        verbose_name_plural = 'Точки'


class GameQueryset(models.QuerySet):
    def finished(self):
        return self.filter(is_over=True)

    def active(self):
        return self.filter(end_date__isnull=False)


class Game(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='games',
                                 verbose_name='Категория')
    user = models.ForeignKey(to='authorization.USer', on_delete=models.CASCADE, related_name='games',
                             verbose_name='Пользователь')
    create_date = models.DateTimeField(auto_now_add=True)
    is_over = models.BooleanField(default=False, verbose_name='Игра закончена')
    score = models.IntegerField(default=0)

    objects = GameQueryset.as_manager()

    def set_score(self):
        scores_in_round = self.rounds.aggregate(scores=Sum('score'))
        self.score = scores_in_round['scores']

    @property
    def round_counts(self):
        return self.rounds.all().count()

    @property
    def used_points_pk(self):
        return list(self.rounds.values_list('random_point__id', flat=True))


class Round(models.Model):
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE, related_name='rounds',
                             verbose_name='Игра')
    random_point = models.ForeignKey(to=Point, on_delete=models.SET_NULL, null=True, default=None,
                                     related_name='rounds', verbose_name='Рандомная точка')
    user_point = models.PointField(null=True, default=None)
    num = models.IntegerField(verbose_name='Номер раунда в игре', null=True, default=None)
    date_start = models.DateTimeField(auto_now_add=True, verbose_name='Время начала раунда')
    date_end = models.DateTimeField(verbose_name='Время окончания раунда', null=True, default=None)
    score = models.IntegerField(default=0, null=True, verbose_name='Очки')


    @property
    def distance_between_points(self):
        assert self.random_point is not None, 'Random point is not define'
        assert self.user_point is not None, 'User point is not define'
        ls = LineString(self.random_point.point, self.user_point, srid=4326)
        ls.transform(ct=54009)
        return ls.length

    def set_score(self):
        value = 5000
        try:
            distance = self.distance_between_points
        except AssertionError:
            value = 0
        else:
            if 150 < distance <= 1000:
                value = 5000 - distance
            elif 1000 < distance <= 100000:
                value = 4000 - distance * 0.001
            elif 100000 < distance <= 500000:
                value = 3000 - distance * 0.002
            elif 500000 < distance:
                value = 2000 - distance * 0.0001
        finally:
            self.score = value if value > 0 else 0

    def set_random_point(self):
        used_points = self.game.used_points_pk
        self.random_point = Point.objects.filter(category=self.game.category).\
            random(exclude_pk=used_points)

    def set_round_num(self):
        self.num = self.game.round_counts


# @receiver(post_save, sender=Round)
# def update_score(sender, instance, created, update_fields, **kwargs):
#     post_save.disconnect(update_score, Round)
#     instance.set_score()
#     instance.game.set_score()
#     post_save.connect(update_score, Round)

