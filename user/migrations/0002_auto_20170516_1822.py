# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-16 10:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='friend_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='friend',
            name='user_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='friend',
            unique_together=set([]),
        ),
    ]