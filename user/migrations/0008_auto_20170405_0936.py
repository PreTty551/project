# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-05 09:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_friend_notify_switch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercontact',
            old_name='first_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='usercontact',
            name='last_name',
        ),
    ]
