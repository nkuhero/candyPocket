# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-07 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0012_packet'),
    ]

    operations = [
        migrations.AddField(
            model_name='packet',
            name='plan',
            field=models.CharField(default='', max_length=200),
        ),
    ]
