# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from accountBook.models import Book, User, SumCost
import datetime, decimal


# Create your views here.


class UserForm(forms.Form): 
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    
class BookForm(forms.Form):
    content = forms.CharField(label='购买项目', max_length=100)
    cost = forms.DecimalField(label='花费', max_digits=10, decimal_places=2)
    cost_date = forms.DateTimeField(label='时间', required=False)
    
#注册
def regist(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获得表单数据
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #添加到数据库
            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist:
                user = User.objects.create(username= username,password=password)
                SumCost.objects.create(user_id=user.id, sum_cost=0)
                return HttpResponse('regist success!!')
            else:
                return HttpResponseRedirect('/account/login/') 
    else:
        uf = UserForm()
    return render_to_response('regist.html',{'uf':uf}, context_instance=RequestContext(req))

#登陆
def login(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获取表单用户密码
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #获取的表单数据与数据库进行比较
            try:
                user = User.objects.get(username = username,password = password)
            except User.DoesNotExist:
                #比较失败，还在login
                error_message = '帐号或密码错误!'
                return render(req, 'login.html', {'error_message':error_message, 'uf': UserForm()})
            #比较成功，跳转index
            response = HttpResponseRedirect('/account/%s/index/' % user.id)
            #将username写入浏览器cookie,失效时间为3600
            #response.set_cookie('username',username,3600)
            req.session['userid'] = user.id
            req.session['username'] = username
            return response
                
    else:
        uf = UserForm()
    return render_to_response('login.html', {'uf':uf}, context_instance=RequestContext(req))

#登陆成功
def index(req, id):
    #登陆校验
    user = User.objects.get(pk=id)
    #username = req.COOKIES.get('username','')
    if req.session.get('userid', default=None) != user.id:
        return HttpResponseRedirect('/account/login/') 

    items = Book.objects.filter(user_id=id).order_by('-cost_date')
    total = SumCost.objects.get(user_id=id)    
    message = None
    if req.method == 'POST':
        cf = BookForm(req.POST)
        if cf.is_valid():
            user_id = user.id
            content = cf.cleaned_data['content']
            cost = cf.cleaned_data['cost']
            cost_date = cf.cleaned_data['cost_date']
            if not cost_date:
                cost_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Book.objects.create(user_id=user_id, content=content, cost=decimal.Decimal(cost), cost_date=cost_date)
            total.sum_cost += decimal.Decimal(cost)
            total.save()
            #message = '记账成功!'
            return HttpResponseRedirect('/account/%s/index/' % user.id) 
            #response = HttpResponse('记录成功')
            #return response
    else:
        cf = BookForm()
    #return render_to_response('index.html' ,{'message':message, 'cf':cf}, context_instance=RequestContext(req))
    return render_to_response('index.html' ,
                              {'username':user.username, 'items':items, 'total_cost':total.sum_cost, 'cf':cf, 'message':message}, 
                              context_instance=RequestContext(req))

#退出
def logout(req):
    response = HttpResponseRedirect('/account/login/')
    #清理cookie里保存username
    #response.delete_cookie('username')
    try:
        del req.session['userid']
    except KeyError:
        pass
    return response