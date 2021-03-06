# Generated by Django 3.2 on 2021-04-16 18:29

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_alter_round_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='date_end',
            field=models.DateTimeField(default=None, null=True, verbose_name='Время окончания раунда'),
        ),
        migrations.AlterField(
            model_name='round',
            name='random_point',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rounds', to='game.point', verbose_name='Рандомная точка'),
        ),
        migrations.AlterField(
            model_name='round',
            name='user_point',
            field=django.contrib.gis.db.models.fields.PointField(default=None, null=True, srid=4326),
        ),
    ]
