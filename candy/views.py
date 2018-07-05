# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import Http404, HttpResponse

from candy.models import Activity, User, Account, Record, Asset, Packet, PacketRecord, RebateRecord, Deposit

import json
import urllib2
import uuid
import redis
import redpackets
import urllib
import execjs
import os

conn = redis.Redis(host='127.0.0.1',port=6379)


url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code'
appId = 'wx8a5e679f92c2aa53'
secret = '177b9c18065aea6793f3de17f049122e'
def get_js():  
    f = open("/root/deposit.js", 'r')  
    line = f.readline()  
    htmlstr = ''  
    while line:  
        htmlstr = htmlstr + line  
        line = f.readline()  
    return htmlstr  


def depositOnline(request):

    os.environ["NODE_PATH"] = "/root/node_modules"
    jsstr = get_js()
    ctx = execjs.compile(jsstr)
    ctx.call('deposit','123456')
    result = {"result": "success"}
    return HttpResponse(json.dumps(result), content_type="application/json")

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
    result = {"session_key" : key, "user_id" : user_id}
 

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


def addUserInfo(request):

    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)

    nickName = request.GET.get("nickName")
    userPic = request.GET.get("userPic")

    user = User.objects.get(user_id=user_id)
    user.userName = nickName
    user.userPic = userPic
    user.save()

    resp = {"code" : 200, "msg" : "success"}
    return HttpResponse(json.dumps(resp), content_type="application/json")



def getPacket(request):

    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)

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
    
    userId = packet.user.user_id
    packetRecord = PacketRecord(user=user, packet=packet, total=prize, userId=userId) 
    packetRecord.save()

    resp = {"code" : 200, "msg" : "success"} 
    return HttpResponse(json.dumps(resp), content_type="application/json")         

def getAssetDesc(request):

    session_key = request.GET.get("session_key")
    user_id = getUserInfo(session_key)
    user = User.objects.get(user_id=user_id)

    activity_id = request.GET.get("activity_id")
    activity = Activity.objects.get(id=activity_id)      
    asset_desc = activity.asset.asset_desc
    asset_name = activity.asset.asset_code

    status = "已抢光" if activity.balance <= 0 else "立即领取"
    record = Record.objects.filter(user=user, activity=activity)
    if record and status != "已抢光":
        status = "已领取"

    resp = {"status": status, "name": asset_name,"desc" : asset_desc, "rebate" : activity.rebate, "total" : activity.total }

    return HttpResponse(json.dumps(resp), content_type="application/json")



def getAssetDescNologin(request):

    asset_code = request.GET.get("asset_code")  
    asset = Asset.objects.get(asset_code=asset_code)

    resp = {"desc" : asset.asset_desc}

    return HttpResponse(json.dumps(resp), content_type="application/json")



def packet(request):


    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)

    asset_code = request.GET.get("asset_code")
    total = float(request.GET.get("total"))
    num = int(request.GET.get("num"))
    packetNo = request.GET.get("packetNo")

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
    
    packet = Packet(user=user, account=account, plan=plan, total=total, num=num, packetNo=packetNo)
    packet.save()

    resp = {"code" : 200, "msg" : "success"}   

    return HttpResponse(json.dumps(resp), content_type="application/json")


def deposit(request):
    
    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)
    user = User.objects.get(user_id=user_id) 
    asset_code = request.GET.get("asset_code")
    address = request.GET.get("address")
    
    asset = Asset.objects.get(asset_code=asset_code)  
    total = float(request.GET.get("total")) 
    account = Account.objects.filter(user=user, asset=asset)[0]
    if total > float(account.balance):
        resp = {"code" : 109, "msg" : "not enough balance"} 
        return HttpResponse(json.dumps(resp), content_type="application/json")     

    account.frozen += total
    account.balance -= total
    account.save()
    depo = Deposit(user=user, account=account, total=total, address=address)
    depo.save()
    resp = {"code" : 200, "msg" : "success"}  
    return HttpResponse(json.dumps(resp), content_type="application/json") 


def getUserPacket(request):

    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)  

    packetNo = request.GET.get("packetNo")     
    packet = Packet.objects.get(packetNo=packetNo)

    packetRecord = PacketRecord.objects.filter(packet=packet)
    userList = []
    for pr in packetRecord:
        
        userList.append({"value" : pr.total * packet.account.asset.asset_cny, "userName" : pr.user.userName, "getDate" : pr.get_date.strftime('%Y-%m-%d %H:%M:%S'), "getDateStamp": pr.get_date,  "total" : pr.total, "pic": pr.user.userPic})

    get_num = len(userList)
    get_value = get_num * packet.account.asset.asset_cny

    resp = {"userList" : userList, "get_value" : get_value, "get_num" : get_num, "packetNo" : packetNo, "userName" : packet.user.userName, "candyName" : packet.account.asset.asset_code, "total" : packet.total, "num" : packet.num,
            
            "pic" : packet.user.userPic, "assetPic" : packet.account.asset.asset_pic}

    return HttpResponse(json.dumps(resp), content_type="application/json")

def getAdminInfo(request):

    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)   

    activityList = Activity.objects.all() 

    activityInfo = []

    for activity in activityList:
        if activity.admin_user == user_id:
            activityInfo.append({"name": activity.name, "pic" : activity.asset.asset_pic, "each" : activity.num_for_every_person, 
                "total" : activity.total , "rebate" : activity.rebate, "balance" : activity.balance, "num" : activity.total / activity.num_for_every_person
                })
 
    resp = {"activityList" : activityInfo}

    return HttpResponse(json.dumps(resp), content_type="application/json")      


def getCandyList(request):
    session_key = request.GET.get("session_key")
    user_id = getUserInfo(session_key)
    user = User.objects.get(user_id=user_id)

    activityList = Activity.objects.all() 
    result = []

    for activity in activityList:
        status = "已抢光" if activity.balance <= 0 else "立即领取"
        record = Record.objects.filter(user=user, activity=activity)
        if record and status != "已抢光":
            status = "已领取"
        result.append({"source" : activity.asset.asset_source, "status" : status, "name" : activity.name, "id" : activity.id, "pic" : activity.asset.asset_pic, "each" : activity.num_for_every_person, "total" : activity.total / activity.num_for_every_person})

    return HttpResponse(json.dumps(result), content_type="application/json") 

def getOneCandy(request):

    activity_id = request.GET.get("activity_id")
    activity = Activity.objects.get(id=activity_id)

    result = {"name" : activity.name, "id" : activity.id, "pic" : activity.asset.asset_pic, "each" : activity.num_for_every_person, "total" : activity.total / activity.num_for_every_person}

    return HttpResponse(json.dumps(result), content_type="application/json") 


def getUserAccountBalance(request):
    session_key = request.GET.get("session_key") 
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

    
def checkAdmin(request):

    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)  

    activityList = Activity.objects.all()  
    hide = "hide"
    for activity in activityList: 
        if  activity.admin_user == user_id:
            hide = "" 

    result =  {"hide" : hide}
    return HttpResponse(json.dumps(result), content_type="application/json") 




def getUserAccount(request):

    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)  

    user = User.objects.get(user_id=user_id)

    account = Account.objects.filter(user=user)

    result = []

    for a in account:
        result.append({"name" : a.asset.asset_code, "balance" : a.balance, "pic" : a.asset.asset_pic, "source" : a.asset.asset_source, "value" : a.balance * a.asset.asset_cny})

    return HttpResponse(json.dumps(result), content_type="application/json") 


def getCandy(request):

    resp = {"code": 200, "msg" : "success"}
 
    session_key = request.GET.get("session_key") 
    user_id = getUserInfo(session_key)   
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
    share_user_id = request.GET.get("share_user_id")
    if share_user_id and share_user_id != user_id:
        share_user = User.objects.get(user_id=share_user_id)
        share_account = Account.objects.filter(user=share_user, asset=asset)[0]
        rebate = activity.rebate
        share_account.balance += rebate
        share_account.save()
        rebateRecord = RebateRecord(user=user, share_user_id=share_user_id, rebate=rebate, activity=activity)
        rebateRecord.save()

    return HttpResponse(json.dumps(resp), content_type="application/json") 
