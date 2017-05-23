# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-23 07:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live', '0002_auto_20170516_2023'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveLockLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=50)),
                ('member_count', models.SmallIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('end_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='end_date')),
            ],
            options={
                'db_table': 'live_lock_log',
            },
        ),
        migrations.AddField(
            model_name='channelmember',
            name='channel_type',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='channelmember',
            name='nickname',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='channelmember',
            name='user_id',
            field=models.IntegerField(db_index=True),
        ),
    ]
