# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-14 17:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0022_account_frozen'),
    ]

    operations = [
        migrations.AddField(
            model_name='deposit',
            name='address',
            field=models.CharField(default='', max_length=200),
        ),
    ]
