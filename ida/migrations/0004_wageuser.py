# -*- coding: utf-8 -*-
<<<<<<< HEAD
<<<<<<< HEAD
# Generated by Django 1.10.6 on 2017-06-13 10:29
=======
# Generated by Django 1.10.6 on 2017-06-13 08:52
>>>>>>> 06ee61a08a7f9f3205bf93fbc086322697d154dc
=======
# Generated by Django 1.10.6 on 2017-06-13 08:52
>>>>>>> 06ee61a08a7f9f3205bf93fbc086322697d154dc
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ida', '0003_auto_20170516_2016'),
    ]

    operations = [
        migrations.CreateModel(
            name='WageUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
    ]
