# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-16 13:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20170516_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='user_id',
            field=models.IntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='friend',
            unique_together=set([('user_id', 'friend_id')]),
        ),
    ]
