from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^getCandy$', views.getCandy),
    url(r'^getCandyList', views.getCandyList),
    url(r'^getUserAccount$', views.getUserAccount),
    url(r'^getUserAccountBalance$', views.getUserAccountBalance),
    url(r'^packet$', views.packet),
    url(r'^login', views.login),

]

