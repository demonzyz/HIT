#coding:utf-8
import sys
import unittest
import HTMLTestRunnerCN
import time
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HIT.settings")
django.setup()
from api.models import *
import http
import random
import string
import base64
import json

class ITest(unittest.TestCase):
    case_list = sys.argv[3].split(',')
    for case_id in case_list:
        case = Case.objects.filter(id=case_id).first()
        FUNC_TEMPLATE = '''def {test_id}(self):
                           '{desc}'
                           ITest.execute_case({data})
                        '''
        exec(FUNC_TEMPLATE.format(test_id='test_'+case.name, desc=case.desc, data=case_id))

    @classmethod
    def execute_case(cls, case_id):
        VALUES = {}  # 用户全局变量
        steps = Step.objects.filter(case=case_id).order_by("order")
        for step in steps:
            print "开始执行测试步骤：",step.name
            template = step.template
            url = template.url
            method = template.method
            t_data_str = template.data
            s_headers_str = step.headers
            s_data_str = step.data
            check_str = step.check
            headers = None
            data = None
            if s_headers_str:
                headers = {}
                for h in s_headers_str.split('&'):
                    key = h.split('=')[0]
                    value = h.split('=')[1]
                    if value.startswith('{{'):
                        value = VALUES.get(value[2:-2], None)
                    headers[key] = value

            if s_data_str and t_data_str:
                t_data = t_data_str.split('&')
                data = {}
                for d in s_data_str.split('&'):
                    key = d.split('=')[0]
                    value = d.split('=')[1]
                    if value.startswith('{{'):
                        value = VALUES.get(value[2:-2], None)
                    data[key] = value
                    if key == 'password':
                        r_str = ''.join(random.sample(string.ascii_letters + string.digits, 3))
                        data[key] = base64.encodestring(r_str+value)
                # 如果步骤中没有指定必填项，赋于模板中维护的默认值
                for p in t_data:
                    if p.split('=')[0] != 'sign' and p.split('=')[0] not in data.keys():
                        data[p.split('=')[0]] = p.split('=')[1]
            # 发送请求
            client = http.client(url=url, method=method, headers=headers, data=data)
            if 'sign' in t_data_str.split('&'):
                client.add_sign()
            client.send()
            # 添加检查点
            if check_str:
                check_list = json.loads(check_str).get("checks", None)
                for check in check_list:
                    try:
                        method_name = check.keys()[0]
                        paras = check[method_name]
                        CHECK_FUNC = "client.{method_name}(paras)"
                        if method_name == 'transfer':
                            VALUES[paras.get('name', None)] = client.transfer(paras.get('path', None))
                        else:
                            eval(CHECK_FUNC.format(method_name=method_name, paras=paras))
                    except Exception, e:
                        assert False, '检查点函数%s执行异常：%s' % (method_name, str(e.message))

if __name__ == '__main__':
    task_id = sys.argv[1]
    task_time = sys.argv[2]
    suite = unittest.defaultTestLoader.discover('./api/', pattern='run.py')
    time_str = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    fp = open('./report/' + time_str + '.html', 'wb')
    HTMLTestRunnerCN.HTMLTestRunner(stream=fp, title='接口自动化测试报告').run(suite)
    History.objects.create(time=task_time, report=os.path.abspath('.')+'\\report\\'+time_str+'.html', status=1, task_id=task_id)
    # unittest.TextTestRunner().run(suite)

