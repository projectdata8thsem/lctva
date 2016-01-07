# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-07 04:33
from __future__ import unicode_literals

from django.db import migrations

from app.models import UserProfile


def set_tz_info(apps, schema_editor):
    for profile in UserProfile.objects.all():
        profile.tz = "America/New_York"
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20160106_2243'),
    ]

    operations = [
        migrations.RunPython(set_tz_info)
    ]
