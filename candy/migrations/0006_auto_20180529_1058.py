# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-29 10:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0005_auto_20180528_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('get_date', models.DateTimeField(auto_now_add=True, verbose_name='get candy')),
            ],
        ),
        migrations.RemoveField(
            model_name='asset',
            name='limit',
        ),
        migrations.AddField(
            model_name='activity',
            name='limit',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='activity',
            name='num_for_every_person',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='record',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candy.Activity'),
        ),
        migrations.AddField(
            model_name='record',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candy.User'),
        ),
    ]
