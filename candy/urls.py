from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^getCandy$', views.getCandy),
    url(r'^getOneCandy$', views.getOneCandy),
    url(r'^getCandyList', views.getCandyList),
    url(r'^getUserAccount$', views.getUserAccount),
    url(r'^getUserAccountBalance$', views.getUserAccountBalance),
    url(r'^getUserPacket', views.getUserPacket),
    url(r'^deposit', views.deposit),
    url(r'^getPacket', views.getPacket),
    url(r'^packet$', views.packet),
    url(r'^login', views.login),
    url(r'^addUserInfo', views.addUserInfo),
    url(r'^checkAdmin', views.checkAdmin),
    url(r'^getAdminInfo', views.getAdminInfo),

]

