# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-12 08:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live', '0004_livelocklog_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livemedialog',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date'),
        ),
    ]