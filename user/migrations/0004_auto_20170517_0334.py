# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-16 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20170516_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitefriend',
            name='invited_id',
            field=models.IntegerField(db_index=True),
        ),
    ]
