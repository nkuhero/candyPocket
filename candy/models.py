# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class User(models.Model):

    user_id = models.CharField(max_length=50)
    join_date = models.DateTimeField('User join', auto_now_add=True)
    

    def __str__(self):
        return self.user_id


@python_2_unicode_compatible
class Asset(models.Model):

    asset_code = models.CharField(max_length=50)
    asset_issuer = models.CharField(max_length=100)
    asset_account = models.CharField(max_length=100, default="")
    asset_pic = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.asset_code + "-" + self.asset_issuer


@python_2_unicode_compatible
class Account(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def __str__(self):         
        return self.user.user_id + "-" + self.asset.asset_code

@python_2_unicode_compatible
class Packet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    total = models.FloatField()                                                                                                                                                                                  
    num = models.IntegerField()
    plan = models.CharField(max_length=200, default="")
    create_date = models.DateTimeField('create packet', auto_now_add=True)
    packetNo = models.CharField(max_length=200, default="")
    userName = models.CharField(max_length=200, default="")    


    def __str__(self):
        return self.user.user_id + "-" + self.packetNo


@python_2_unicode_compatible
class PacketRecord(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    packet = models.ForeignKey(Packet, on_delete=models.CASCADE)
    total = models.FloatField()    
    get_date = models.DateTimeField('get packet', auto_now_add=True)
    userName = models.CharField(max_length=200, default="")    


    def __str__(self):
        return self.user.user_id + "-" + self.packet.packetNo

@python_2_unicode_compatible
class Activity(models.Model):

    name = models.CharField(max_length=50, default="") 
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    start = models.BooleanField(default=False)
    num_for_every_person = models.FloatField(default=0) 
    total = models.FloatField(default=0)  
    balance = models.FloatField(default=0)
    rebate = models.FloatField(default=0)
    def __str__(self):       
        return self.name

@python_2_unicode_compatible
class RebateRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    share_user_id = models.CharField(max_length=200, default="")     
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    get_date = models.DateTimeField('get candy', auto_now_add=True) 
    rebate = rebate = models.FloatField(default=0)  

    def __str__(self):
        return self.share_user_id + "-" + self.activity.activity_id

@python_2_unicode_compatible
class Record(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    get_date = models.DateTimeField('get candy', auto_now_add=True)
    num = models.FloatField(default=0) 

    def __str__(self):
        return self.user.user_id + "-" + self.activity.name
