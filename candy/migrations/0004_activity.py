# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-24 10:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0003_asset_asset_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.BooleanField(default=False)),
                ('asset_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candy.Asset')),
            ],
        ),
    ]