# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-05 08:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0003_auto_20170402_1054'),
    ]

    operations = [
        migrations.RenameField(
            model_name='walletrecord',
            old_name='order_id',
            new_name='out_trade_no',
        ),
    ]
