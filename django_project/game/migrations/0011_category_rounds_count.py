# Generated by Django 3.2 on 2021-04-16 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_rename_game_over_game_is_over'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='rounds_count',
            field=models.IntegerField(default=1, verbose_name='Число раундов'),
            preserve_default=False,
        ),
    ]