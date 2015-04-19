# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from accountBook import views

urlpatterns = patterns('',
    url(r'^$', views.login, name='login'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^regist/$', views.regist, name = 'regist'),
    #/1/index
    url(r'^(?P<id>\d+)/index/$', views.index, name = 'index'),
    url(r'^(?P<id>\d+)/index/(?P<page_num>\d+)/$', views.index, name = 'index'),
    url(r'^updateView/(?P<id>\d+)/$', views.updateView, name = 'updateView'),
    url(r'^update/$', views.update, name = 'update'),
    url(r'^delete/(?P<id>\d+)/$', views.delete, name = 'delete'),
    url(r'^logout/$', views.logout, name = 'logout'),
)