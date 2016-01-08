# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-08 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20160108_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderboard',
            name='monthly',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='leaderboard',
            name='date',
            field=models.DateField(db_index=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='leaderboard',
            unique_together=set([('date', 'monthly')]),
        ),
    ]
