from django.contrib import admin
from accountBook.models import User, Book, SumCost

# Register your models here.

admin.site.register(User)
admin.site.register(Book)
admin.site.register(SumCost)