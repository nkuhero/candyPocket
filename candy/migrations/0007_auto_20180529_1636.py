# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-29 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0006_auto_20180529_1058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activity',
            old_name='limit',
            new_name='balance',
        ),
        migrations.AddField(
            model_name='activity',
            name='total',
            field=models.FloatField(default=0),
        ),
    ]
