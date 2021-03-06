# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-05 07:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('channel_id', models.CharField(max_length=50, unique=True)),
                ('creator_id', models.IntegerField(default=0)),
                ('member_count', models.SmallIntegerField(default=0)),
                ('channel_type', models.SmallIntegerField(default=0)),
                ('is_lock', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
            ],
            options={
                'db_table': 'channel',
            },
        ),
        migrations.CreateModel(
            name='ChannelMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_id', models.CharField(max_length=50)),
                ('user_id', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
            ],
            options={
                'db_table': 'channel_member',
            },
        ),
        migrations.CreateModel(
            name='GuessWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
            ],
        ),
        migrations.CreateModel(
            name='InviteParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('to_user_id', models.IntegerField()),
                ('channel_id', models.CharField(default='', max_length=50)),
                ('party_type', models.SmallIntegerField(default=0)),
                ('status', models.SmallIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
            ],
            options={
                'db_table': 'invite_party',
            },
        ),
        migrations.CreateModel(
            name='LiveMediaLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('channel_id', models.CharField(max_length=50)),
                ('status', models.SmallIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('end_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='end_date')),
            ],
            options={
                'db_table': 'live_media_log',
            },
        ),
        migrations.AlterUniqueTogether(
            name='channelmember',
            unique_together=set([('channel_id', 'user_id')]),
        ),
    ]
