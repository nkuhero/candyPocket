# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


from .models import User, Account, Asset, Activity, Record, Packet

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Asset)
admin.site.register(Activity)
admin.site.register(Record)
admin.site.register(Packet)


# Register your models here.
