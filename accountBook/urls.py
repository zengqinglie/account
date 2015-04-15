# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from accountBook import views

urlpatterns = patterns('',
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^regist/$', views.regist, name = 'regist'),
    #/1/index
    url(r'^(?P<id>\d+)/index/$', views.index, name = 'index'),
    #url(r'^index/$', views.index, name = 'index'),
    url(r'^logout/$', views.logout, name = 'logout'),
)