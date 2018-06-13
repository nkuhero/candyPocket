# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import Http404, HttpResponse

from candy.models import Activity, User, Account, Record, Asset, Packet, PacketRecord, RebateRecord

import json
import urllib2
import uuid
import redis
import redpackets
import urllib

conn = redis.Redis(host='127.0.0.1',port=6379)


url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code'
appId = 'wx8a5e679f92c2aa53'
secret = '177b9c18065aea6793f3de17f049122e'


def login(request):
 
    code = request.GET.get("code") 
    response = urllib2.urlopen(url%(appId, secret, code))
    content = json.loads(response.read())
    #key = str(uuid.uuid1())
    user_id = content["openid"] 
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist: 
        user = User(user_id=user_id)
        user.save()
    #conn.set(key, json.dumps(content))
    result = {"user_id" : user_id}

   
    

    return HttpResponse(json.dumps(result), content_type="application/json")



def getUserInfo(session_key):

    userInfo = conn.get(session_key)
    print userInfo
    if not userInfo:
        return None
    else:
        user_id = json.loads(userInfo)["openid"]
        return user_id



def checkUserLogin(request):

    session_key = request.GET.get("session_key")
    user_id = getUserInfo(session_key) 
    if not user_id:
        resp = {"code" : 103, "msg" : "User does not login"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        return None    



def getPacket(request):

    user_id = request.GET.get("user_id")

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist: 
        user = User(user_id=user_id)
        user.save()

    packetNo = request.GET.get("packetNo")
    packet = Packet.objects.get(packetNo=packetNo)
    
    plan = packet.plan
    if not plan:
        resp = {"code" : 105, "msg" : "packet runs out"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    packetRecord = PacketRecord.objects.filter(user=user, packet=packet)
    if packetRecord:
        resp = {"code" : 106, "msg" : "already get this packet"} 
        return HttpResponse(json.dumps(resp), content_type="application/json")

    asset_code = request.GET.get("asset_code")  
    asset = Asset.objects.get(asset_code=asset_code)
    account = Account.objects.filter(user=user, asset=asset)[0]
    try:
        account = Account.objects.filter(user=user, asset=asset)[0]
    except: 
        account = Account(user=user, asset=asset)
        account.save()

    planList = plan.split(',')
    prize  = planList.pop()
    plan = ",".join(planList)

    account.balance += float(prize)
    account.save()
    packet.plan = plan
    packet.save()
    userName = urllib.unquote(request.GET.get('userName'))

    packetRecord = PacketRecord(user=user, packet=packet, total=prize, userName=userName) 
    packetRecord.save()

    resp = {"code" : 200, "msg" : "success"} 
    return HttpResponse(json.dumps(resp), content_type="application/json")         



def packet(request):

    user_id = request.GET.get("user_id")
 
    asset_code = request.GET.get("asset_code")
    total = float(request.GET.get("total"))
    num = int(request.GET.get("num"))
    packetNo = request.GET.get("packetNo")
    userName = urllib.unquote(request.GET.get('userName'))

    user = User.objects.get(user_id=user_id)
    asset = Asset.objects.get(asset_code=asset_code)  
    account = Account.objects.filter(user=user, asset=asset)[0]
    if account.balance < total:
        resp = {"code" : 104, "msg" : "balance is not enough"}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    else:
        account.balance -= total
        account.save()

    li = redpackets.split(total, num, min=0.01)       
    plan = ",".join([str(x) for x in li])
    
    packet = Packet(user=user, account=account, plan=plan, total=total, num=num, packetNo=packetNo, userName=userName)
    packet.save()

    resp = {"code" : 200, "msg" : "success"}   

    return HttpResponse(json.dumps(resp), content_type="application/json")

def getUserPacket(request):
    user_id = request.GET.get("user_id")

    packetNo = request.GET.get("packetNo")     
    packet = Packet.objects.get(packetNo=packetNo)

    packetRecord = PacketRecord.objects.filter(packet=packet)
    userList = []
    for pr in packetRecord:
        userList.append({"userName" : pr.userName, "getDate" : pr.get_date.strftime('%Y-%m-%d %H:%M:%S'), "total" : pr.total})

    get_num = len(userList)

    resp = {"userList" : userList, "get_num" : get_num, "packetNo" : packetNo, "userName" : packet.userName, "candyName" : packet.account.asset.asset_code, "total" : packet.total, "num" : packet.num}

    return HttpResponse(json.dumps(resp), content_type="application/json")


def getCandyList(request):

    activityList = Activity.objects.all() 
    result = []

    for activity in activityList:
        status = "已抢光" if activity.balance <= 0 else ""
            
        result.append({"status" : status, "name" : activity.name, "id" : activity.id, "pic" : activity.asset.asset_pic, "each" : activity.num_for_every_person, "total" : activity.total / activity.num_for_every_person})

    return HttpResponse(json.dumps(result), content_type="application/json") 

def getOneCandy(request):

    activity_id = request.GET.get("activity_id")
    activity = Activity.objects.get(id=activity_id)

    result = {"name" : activity.name, "id" : activity.id, "pic" : activity.asset.asset_pic, "each" : activity.num_for_every_person, "total" : activity.total / activity.num_for_every_person}

    return HttpResponse(json.dumps(result), content_type="application/json") 


def getUserAccountBalance(request):
    user_id = request.GET.get("user_id")

    if not user_id:
        resp = {"code" : 103, "msg" : "User does not login"}
        return HttpResponse(json.dumps(resp), content_type="application/json")

    asset_code = request.GET.get("asset_code")


    user = User.objects.get(user_id=user_id)

    asset = Asset.objects.get(asset_code=asset_code)

    account = Account.objects.filter(user=user, asset=asset)[0]

    result =  {"balance" : account.balance}

    return HttpResponse(json.dumps(result), content_type="application/json") 

    


def getUserAccount(request):
    user_id = request.GET.get("user_id")

    user = User.objects.get(user_id=user_id)

    account = Account.objects.filter(user=user)

    result = []

    for a in account:
        result.append({"name" : a.asset.asset_code, "balance" : a.balance, "pic" : a.asset.asset_pic})

    return HttpResponse(json.dumps(result), content_type="application/json") 


def getCandy(request):

    resp = {"code": 200, "msg" : "success"}
  
    user_id = request.GET.get("user_id")
    activity_id = request.GET.get("activity_id")
    
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        resp = {"code" : 100, "msg" : "User does not exist"}
        return HttpResponse(json.dumps(resp), content_type="application/json") 
    


    activity = Activity.objects.get(pk=activity_id)

    record = Record.objects.filter(user=user, activity=activity)

    #每个用户一个活动只能参与一次
    if record:
        resp = {"code" : 101, "msg" : "User already get the candy"}   
        return HttpResponse(json.dumps(resp), content_type="application/json") 

    asset = activity.asset

    account = Account.objects.filter(user=user, asset=asset)

    if not account:
        account = Account(user=user, asset=asset)
        account.save()
    else:
        account = account[0]

    if activity.balance >= activity.num_for_every_person:
        account.balance += activity.num_for_every_person
        activity.balance -= activity.num_for_every_person
    else:
        resp = {"code" : 102, "msg" : "Activity's balance runs out"}   
        return HttpResponse(json.dumps(resp), content_type="application/json") 

    record = Record(user=user, activity=activity, num=activity.num_for_every_person)    
   
    account.save()
    activity.save()
    record.save()
    share_user_id = request.GET.get("activity_id")
    if share_user_id and share_user_id != user_id:
        share_user = User.objects.get(user_id=share_user_id)
        rebate = activity.rebate
        share_user.balance += rebate
        share_user.save()

    return HttpResponse(json.dumps(resp), content_type="application/json") 
