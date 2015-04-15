# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username

class Book(models.Model):
    user = models.ForeignKey(User)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    content = models.CharField(max_length=100)
    cost_date = models.DateTimeField()
    
    def __str__(self):
        return self.content
    
class SumCost(models.Model):
    user = models.ForeignKey(User)
    sum_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.user.username


    
    