# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-05 11:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20170518_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDynamic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('nickname', models.CharField(max_length=50)),
                ('avatar', models.CharField(default='', max_length=40)),
                ('is_paing', models.BooleanField(default=False)),
                ('last_pa_time', models.DateTimeField()),
                ('update_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
