# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-10 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gift', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gift',
            name='message',
            field=models.CharField(default='', max_length=50),
        ),
    ]