# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-15 09:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('candy', '0025_activity_admin_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='packetrecord',
            old_name='userName',
            new_name='userId',
        ),
        migrations.RemoveField(
            model_name='packet',
            name='userName',
        ),
    ]
