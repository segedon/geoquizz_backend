# Generated by Django 3.2 on 2021-04-16 18:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_round'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='scores',
        ),
        migrations.RemoveField(
            model_name='round',
            name='score',
        ),
    ]
