#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from api.models import *
from rest_framework.decorators import api_view
# Create your views here.


def home(requset):
    return render(requset, 'home.html')

def task(requset):
    #返回所有测试任务数据
    tasks = Task.objects.all()
    for task in tasks:
        print task.name
    return render(requset, 'task.html', {"tasks": tasks})


# @api_view(['GET'])
# def task_delete(request):
#     id = request.GET.get('id', None)
#     task = Task.objects.filter(id=id)
#     if task.exists():
#         task.delete()
#         tasks = Task.objects.all()
#     return render(request, 'task.html', {"tasks": tasks})
