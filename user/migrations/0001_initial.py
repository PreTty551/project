# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-24 14:42
from __future__ import unicode_literals

import corelib.props
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone
import user.models.user


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('paid', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('nickname', models.CharField(max_length=50)),
                ('mobile', models.CharField(max_length=20, unique=True)),
                ('avatar', models.CharField(default='', max_length=20)),
                ('gender', models.SmallIntegerField(default=0)),
                ('intro', models.CharField(default='', max_length=100)),
                ('country', models.CharField(default='', max_length=20)),
                ('country_code', models.CharField(default='', max_length=10)),
                ('is_contact', models.BooleanField(default=False)),
                ('platform', models.SmallIntegerField(default=0)),
                ('version', models.CharField(default='', max_length=10)),
                ('pinyin', models.CharField(default='', max_length=50)),
                ('online_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('offline_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('rong_token', models.CharField(default='', max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户列表',
                'db_table': 'user',
            },
            bases=(models.Model, corelib.props.PropsMixin),
            managers=[
                ('objects', user.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BanUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('desc', models.CharField(max_length=200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('second', models.IntegerField()),
            ],
            options={
                'db_table': 'ban_user',
            },
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('friend_id', models.IntegerField()),
                ('invisible', models.BooleanField(default=False)),
                ('push', models.BooleanField(default=True)),
                ('memo', models.CharField(default='', max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ignore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('type', models.SmallIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='InviteFriend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('invited_id', models.IntegerField()),
                ('status', models.SmallIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TempThirdUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('third_id', models.CharField(max_length=30)),
                ('third_name', models.CharField(max_length=20)),
                ('gender', models.SmallIntegerField(default=0)),
                ('nickname', models.CharField(max_length=50)),
                ('avatar', models.CharField(max_length=255)),
                ('wx_unionid', models.CharField(default='', max_length=50)),
                ('user_id', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'temp_third_user',
            },
        ),
        migrations.CreateModel(
            name='ThirdUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(db_index=True, default=0, max_length=20)),
                ('third_id', models.CharField(max_length=30)),
                ('third_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'third_user',
            },
        ),
        migrations.CreateModel(
            name='UserContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(db_index=True)),
                ('name', models.CharField(max_length=50)),
                ('mobile', models.CharField(db_index=True, max_length=20)),
            ],
            options={
                'db_table': 'user_contact',
            },
        ),
        migrations.AlterUniqueTogether(
            name='invitefriend',
            unique_together=set([('invited_id', 'user_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='friend',
            unique_together=set([('user_id', 'friend_id')]),
        ),
    ]
