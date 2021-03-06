# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-05 07:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(unique=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=11)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WalletRecharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('out_trade_no', models.CharField(max_length=100, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.SmallIntegerField(default=0)),
            ],
            options={
                'db_table': 'wallet_recharge',
            },
        ),
        migrations.CreateModel(
            name='WalletRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_id', models.IntegerField(default=0)),
                ('user_id', models.IntegerField()),
                ('out_trade_no', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('category', models.SmallIntegerField(default=0)),
                ('type', models.SmallIntegerField()),
                ('desc', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=200)),
                ('user_id', models.IntegerField()),
                ('status', models.SmallIntegerField(default=0)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('wechat_recode', models.CharField(default='', max_length=50)),
            ],
            options={
                'db_table': 'wallet_withdrawal',
            },
        ),
    ]
