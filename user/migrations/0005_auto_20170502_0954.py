# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-02 09:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20170428_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='is_hint',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='friend',
            name='update_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]