from django.contrib.gis.db import models


class Category(models.Model):
    codename = models.CharField(max_length=20, verbose_name='Кодовое имя')
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Картинка')

    @property
    def points_count(self):
        return self.points.all().count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Point(models.Model):
    point = models.PointField(verbose_name='Точка')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='points',
                                 verbose_name='Категория')

    def __str__(self):
        return '{} {}'.format(self.category.name, self.pk)

    class Meta:
        verbose_name = 'Точка'
        verbose_name_plural = 'Точки'


