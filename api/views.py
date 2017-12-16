# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from  rest_framework.decorators import api_view
from api.models import *
import json
from django.db import  connection
import os


@api_view(['POST'])
def add_template(request):
    name = request.POST.get('name', None)
    url = request.POST.get('url', None)
    method = request.POST.get('method', None)
    if name and url and method:
        if not Template.objects.filter(name=name).exists():
            headers = request.POST.get('headers', None)
            data = request.POST.get('data', None)
            desc = request.POST.get('desc', None)
            template = Template(name=name, url=url,
                                method=method, headers=headers, data=data, desc=desc)
            template.save()
            result = {'error_code': 0, 'template_id': template.id}
        else:
            result = {'error_code': 10002}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)

@api_view(['GET'])
def get_list(request):
    temolate = Template.objects.filter().all()
    if temolate.count() > 0:
        template_list = []
        for key in temolate:
            key_list = {}
            key_list['id'] = key.id
            key_list['name'] = key.name
            key_list['desc'] = key.desc
            template_list.append(key_list)
        result = {'error_code': 0, 'template_list': template_list}
    else:
        result = {'error_code': 10003}
    return HttpResponse(content_type='application/json', content=json.dumps(result, ensure_ascii=False))


@api_view(['POST'])
def add_case(request):
    name = request.POST.get('name', None)
    desc = request.POST.get('desc', None)
    status = request.POST.get('status', None)
    print name
    if name:
        if not Case.objects.filter(name=name).exists():
            print desc
            case = Case(name=name, desc=desc, status=status)
            print status
            case.save()
            result = {'error_code': 0, 'case_id': case.id}
        else:
            result ={'error_code': 10006}
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
                step = Step(name=name, order=order, check=check,case=case.first(),
                            template=template.first(), headers=headers, data=data)
                step.save()
                result = {'error_code': 0, 'step_id': step.id}
            else:
                result = {'error_code': 10005}
        else:
            result = {'error_code': 10004}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)


@api_view(['POST'])
def add_task(request):
    name = request.POST.get('name', None)
    cases = request.POST.get('cases', None)
    desc = request.POST.get('desc', None)
    if name and cases:
        if not Task.objects.filter(name=name).exists():
            task = Task(name=name, desc=desc)
            task.save()
            case_list = cases.split(',')
            for c_id in case_list:
                c = Case.objects.filter(id=c_id)
                if c.exists():
                    task.case.add(c.first())
                else:
                    result = {'error_code': 10007}
                    break
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
            cursor = connection.cursor()
            sql = 'SELECT case_id FROM api_task_case WHERE task_id=%s' % task_id
            if cursor.execute(sql) > 0:
                for case in cursor.fetchall():
                    case_id = case[0]
                    if Case.objects.filter(id=case_id).first().status == 0:
                        case_list.append(str(case_id))
            cursor.close
            if len(case_list) > 0:
                case_str = ','.join(case_list)
                os.system('python ./api/run.py %s' % case_str)
            else:
                result = {'error_code': 10010, 'info': '没有可执行的测试用例'}
            result = {'error_code': 0}
        else:
            result = {'error_code': 10009}
    else:
        result = {'error_code': 10001}
    return JsonResponse(result)