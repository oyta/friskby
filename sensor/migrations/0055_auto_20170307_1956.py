# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 18:56
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0054_rawdata_s_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='sensor_id',
            field=models.CharField(max_length=60, unique=True, validators=[django.core.validators.RegexValidator(regex=b'^[-_:a-zA-Z0-9]+$')], verbose_name=b'Sensor ID'),
        ),
    ]