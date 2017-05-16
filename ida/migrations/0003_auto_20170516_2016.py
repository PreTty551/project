# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-16 12:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ida', '0002_auto_20170515_1921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='duty',
            name='mobile',
        ),
        migrations.RemoveField(
            model_name='duty',
            name='name',
        ),
        migrations.AddField(
            model_name='duty',
            name='memo',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='duty',
            name='group',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]