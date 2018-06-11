# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import Http404, HttpResponse

from candy.models import Activity, User, Account, Record, Asset, Packet

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
    key = str(uuid.uuid1())
    user_id = content["openid"] 
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist: 
        user = User(user_id=user_id)
        user.save()
    conn.set(key, json.dumps(content))
    result = {"session_key" : key}

   
    

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


def packet(request):

    session_key = request.GET.get("session_key")
 
    userNotLogin = checkUserLogin(request)
    if userNotLogin:
        return userNotLogin

    user_id = getUserInfo(session_key)
    asset_code = request.GET.get("asset_code")
    total = float(request.GET.get("total"))
    num = int(request.GET.get("num"))
    packetNo = request.GET.get("packetNo")
    userName = urllib.unquote(request.GET.get('userName')).decode('utf8')

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

def getCandyList(request):

    activityList = Activity.objects.all() 
    result = []

    for activity in activityList:
        status = "已抢光" if activity.balance <= 0 else ""
            
        result.append({"status" : status, "name" : activity.name, "id" : activity.id, "pic" : activity.asset.asset_pic, "each" : activity.num_for_every_person, "total" : activity.total / activity.num_for_every_person})

    return HttpResponse(json.dumps(result), content_type="application/json") 



def getUserAccountBalance(request):

    session_key = request.GET.get("session_key")

    userNotLogin = checkUserLogin(request)
    if userNotLogin:
        return userNotLogin

    user_id = getUserInfo(session_key)

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

    session_key = request.GET.get("session_key")

    userNotLogin = checkUserLogin(request)
    if userNotLogin:       
        return userNotLogin 

    user_id = getUserInfo(session_key)

    user = User.objects.get(user_id=user_id)

    account = Account.objects.filter(user=user)

    result = []

    for a in account:
        result.append({"name" : a.asset.asset_code, "balance" : a.balance, "pic" : a.asset.asset_pic})

    return HttpResponse(json.dumps(result), content_type="application/json") 


def getCandy(request):

    resp = {"code": 200, "msg" : "success"}
  
    session_key = request.GET.get("session_key")
    activity_id = request.GET.get("activity_id")

    
    userNotLogin = checkUserLogin(request)
    if userNotLogin:       
        return userNotLogin 

    user_id = getUserInfo(session_key)
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

    return HttpResponse(json.dumps(resp), content_type="application/json") 
