# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


from .models import User, Account, Asset, Activity, Record, Packet, PacketRecord, RebateRecord, Deposit

admin.site.register(User)
admin.site.register(Account)
admin.site.register(Asset)
admin.site.register(Activity)
admin.site.register(Record)
admin.site.register(Packet)
admin.site.register(PacketRecord)
admin.site.register(RebateRecord)
admin.site.register(Deposit)


# Register your models here.
