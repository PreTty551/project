# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-14 09:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_friend_memo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='paid',
            field=models.CharField(db_index=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='pinyin',
            field=models.CharField(default='', max_length=30),
        ),
    ]
