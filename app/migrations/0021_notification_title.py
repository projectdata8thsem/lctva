# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-07 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20160107_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
    ]
