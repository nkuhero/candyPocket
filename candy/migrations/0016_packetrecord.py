# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-11 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0015_packet_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='PacketRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.FloatField()),
                ('get_date', models.DateTimeField(auto_now_add=True, verbose_name='get packet')),
                ('packet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candy.Packet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='candy.User')),
            ],
        ),
    ]
