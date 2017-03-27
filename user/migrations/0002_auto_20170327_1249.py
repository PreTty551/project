# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-27 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempThirdUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('third_id', models.CharField(max_length=30)),
                ('third_name', models.CharField(max_length=20)),
                ('gender', models.SmallIntegerField(default=0)),
                ('nickname', models.CharField(max_length=20)),
                ('avatar', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'temp_third_user',
            },
        ),
        migrations.AlterField(
            model_name='thirduser',
            name='mobile',
            field=models.CharField(db_index=True, default=0, max_length=20),
        ),
    ]
