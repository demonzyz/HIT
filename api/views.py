#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from api.models import *
import json
from django.db import connection
import os
import time

@api_view(['POST'])
def add_template(request):
    name = request.POST.get('name', None)
    url = request.POST.get('url', None)
    method = request.POST.get('method', None)
    if name and url and method:
        if not Template.objects.filter(name=name).exists():
            headers = request.POST.get('headers', None)
            data = request.POST.get('data', None)
            template = Template(name=name, url=url,
                     method=method, headers=headers, data=data)
            template.save()
            result = {'error_code': 0, 'template_id': template.id}
        else:
            result = {'error_code': 10002}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)

@api_view(['GET', 'POST'])
def get_template_list(request):
    templates = Template.objects.filter().all()
    if templates.exists():
        list = []
        for t in templates:
            t_dic = {'id': t.id, 'name': t.name, 'desc': t.desc}
            list.append(t_dic)
        result = {'error_code': 0, 'template_list': list}
    else:
        result = {'error_code': 10003}
    return HttpResponse(content_type='application/json', content=json.dumps(result, ensure_ascii=False))

@api_view(['POST'])
def add_case(request):
    name = request.POST.get('name', None)
    desc = request.POST.get('desc', None)
    status = request.POST.get('status', None)
    if name:
        if not Case.objects.filter(name=name).exists():
            case = Case(name=name, desc=desc, status=status)
            case.save()
            result = {'error_code': 0, 'case_id': case.id}
        else:
            result = {'error_code': 10006}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)

@api_view(['POST'])
def add_step(request):
    name = request.POST.get('name', None)
    order = request.POST.get('order', None)
    check = request.POST.get('check', None)
    case_id = request.POST.get('case', None)
    template_id = request.POST.get('template', None)
    headers = request.POST.get('headers', None)
    data = request.POST.get('data', None)
    if name and order and case_id and template_id:
        template = Template.objects.filter(id=template_id)
        if template.exists():
            case = Case.objects.filter(id=case_id)
            if case.exists():
                step = Step(name=name, order=order, check=check,
                     case=case.first(), template=template.first(), headers=headers,
                     data=data)
                step.save()
                result = {'error_code': 0, 'step_id': step.id}
            else:
                result = {'error_code': 10005}
        else:
            result = {'error_code': 10004}
    else:
        result = {'error_code': 10001}
    return  JsonResponse(result)

@api_view(['POST'])
def add_task(request):
    name = request.POST.get('name', None)
    desc = request.POST.get('desc', None)
    cases = request.POST.get('cases', None)
    if name and cases:
        if not Task.objects.filter(name=name).exists():
            task = Task(name=name, desc=desc)
            task.save()
            cases_list = cases.split(',')
            for c_id in cases_list:
                c = Case.objects.filter(id=c_id)
                if c.exists():
                    task.case.add(c.first())
                else:
                    break
                    result = {'error_code': 10007}
                result = {'error_code': 0, 'task_id': task.id}
        else:
            result = {'error_code': 10008}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)

@api_view(['POST', 'GET'])
def run_task(request):
    task_id = request.REQUEST.get('id', None)
    if task_id:
        if Task.objects.filter(id=task_id).exists():
            case_list = []
            # 获取到所有测试用例，判断是否存在，是否可运行
            cursor = connection.cursor()
            sql = "select case_id from api_task_case where task_id=%s"%task_id
            if cursor.execute(sql)>0:
                cases = cursor.fetchall()
                for case_id in cases:
                   case = Case.objects.filter(id=case_id[0])
                   if case.exists() and case.first().status == 0:
                       case_list.append(str(case.first().id))
                       case_list_str = ','.join(case_list)
                if len(case_list) > 0:
                    time_temp = time.time()
                    status = os.system("python ./api/run.py %s %f %s" % (task_id, time_temp, case_list_str))
                    if status == 0:
                        # 轮询任务历史表中知否存在报告信息
                        flag = 0
                        while(flag < 10):
                            his = History.objects.filter(time=time_temp)
                            if his.exists():
                                result = {'error_code': 0, "report_path":his.first().report}
                                return JsonResponse(result)
                            else:
                                flag+=1
                                time.sleep(1)
                        result = {'error_code': 10010, 'info': '超时无法获取报告地址'}
                    else:
                        result = {'error_code': 10010}
                # 没有可运行的用例
                else:
                    result = {'error_code': 10010, 'info': '无可执行的测试用例'}
            else:
                result = {'error_code': 10010, 'info':'无可执行的测试用例'}
        else:
            result = {'error_code': 10009}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)