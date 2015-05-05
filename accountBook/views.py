# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django import forms
from accountBook.models import Book, User, SumCost
from django.core.paginator import Paginator
from django.db.models import Sum
import datetime, decimal, calendar


# Create your views here.


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

class BookForm(forms.Form):
    content = forms.CharField(label='购买项目', max_length=100)
    cost = forms.DecimalField(label='花费', max_digits=10, decimal_places=2)
    cost_date = forms.DateTimeField(label='时间', required=False, widget=forms.DateTimeInput(attrs={'class': 'laydate-icon'}))

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
def index(req, id, page_num=1):
    #登陆校验
    user = User.objects.get(pk=id)
    #username = req.COOKIES.get('username','')
    if req.session.get('userid', default=None) != user.id:
        return HttpResponseRedirect('/account/login/')

    #当前日期
    today = datetime.datetime.now().date()
    month = today.month
    year = today.year
    day = today.day

    #按天统计
    today_start = datetime.datetime(year, month, day, 0, 0, 0)
    today_end = datetime.datetime(year, month, day, 23, 59, 59)
    day_cost_sum = Book.objects.filter(user_id=id, cost__gt=0, cost_date__range=(today_start, today_end)).aggregate(Sum('cost'))
    if not day_cost_sum['cost__sum']:
        day_cost_sum['cost__sum'] = 0

    #获取本周起止时间
    weekday = today.weekday()
    monday = today - datetime.timedelta(weekday)
    sunday = monday + datetime.timedelta(6)
    
    #按周统计
    week_start = monday
    week_end = datetime.datetime(year, month, sunday.day, 23, 59, 59)
    week_cost_sum = Book.objects.filter(user_id=id, cost__gt=0, cost_date__range=(week_start, week_end)).aggregate(Sum('cost'))
    if not week_cost_sum['cost__sum']:
        week_cost_sum['cost__sum'] = 0

    #获取本月时间
    month_start = datetime.date(year, month, 1)
    month_end = datetime.date(year, month, calendar.monthrange(year, month)[1])
    #统计本月
    month_cost_sum = Book.objects.filter(user_id=id, cost__gt=0, cost_date__range=(month_start, month_end)).aggregate(Sum('cost'))
    if not month_cost_sum['cost__sum']:
        month_cost_sum['cost__sum'] = 0
    #本月收入
    month_earn_sum = Book.objects.filter(user_id=id, cost__lt=0, cost_date__range=(month_start, month_end)).aggregate(Sum('cost'))
    if not month_earn_sum['cost__sum']:
        month_earn_sum['cost__sum'] = 0
    #累计收入
    total_earn_sum = Book.objects.filter(user_id=id, cost__lt=0).aggregate(Sum('cost'))
    if not total_earn_sum['cost__sum']:
        total_earn_sum['cost__sum'] = 0


    #获取分页展示列表
    user_id = user.id
    items = Book.objects.filter(user_id=id).order_by('-cost_date')
    total = SumCost.objects.get(user_id=id)
    p = Paginator(items, 10)
    book_page = p.page(page_num)
    message = None

    #记账表单处理
    if req.method == 'POST':
        cf = BookForm(req.POST)
        if cf.is_valid():
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
                              {'user_id':user_id,
                               'username':user.username,
                               'book_page':book_page,
                               'p':p,
                               'total_cost':total.sum_cost,
                               'cf':cf,
                               'message':message,
                               'day_cost_sum':day_cost_sum['cost__sum'],
                               'week_cost_sum':week_cost_sum['cost__sum'],
                               "month_cost_sum":month_cost_sum['cost__sum'],
                               "month_earn_sum":abs(month_earn_sum['cost__sum']),
                               "total_earn_sum":abs(total_earn_sum['cost__sum']),
                               },
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

#修改页面
def updateView(req, id):
    #登陆校验
    item = get_object_or_404(Book, pk=int(id))
    return render_to_response('update_book.html', {'cf': item}, context_instance=RequestContext(req))

def update(req):
    user_id = req.session.get('userid')
    id = req.POST['id']
    content = req.POST['content']
    cost = req.POST['cost']
    cost_date = req.POST['cost_date']
    item = get_object_or_404(Book, pk=int(id))
    total = SumCost.objects.get(user_id=user_id)
    st = decimal.Decimal(cost) - decimal.Decimal(item.cost)
    total.sum_cost += st
    total.save()
    item.content = content
    item.cost = decimal.Decimal(cost)
    item.cost_date = cost_date
    item.save()
    return HttpResponseRedirect('/account/%s/index' % user_id)

#删除
def delete(req, id):
    user_id = req.session.get('userid')
    item = get_object_or_404(Book, pk=int(id))
    total = SumCost.objects.get(user_id=user_id)
    total.sum_cost -= decimal.Decimal(item.cost)
    total.save()
    item.delete()
    return HttpResponseRedirect('/account/%s/index' % user_id)
