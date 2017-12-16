#coding:utf-8
import sys
import unittest
import HTMLTestRunnerCN
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HIT.settings")
django.setup()
from api.models import *
import http
import base64
import hashlib
import random
import string
import json


class ITest(unittest.TestCase):
    cases_id = sys.argv[1].split(',')
    for case_id in cases_id:
        case = Case.objects.filter(id=case_id)
        if case.exists():
            FUNCTION = '''def test_{case_name}(self): 
                        '{desc}' 
                        ITest.build_case({case_id})
                        '''
            exec(FUNCTION.format(case_name=case.first().name,
                                desc=case.first().desc,
                                case_id=case_id
                                ))

    @classmethod
    def build_case(cls, case_id):
        VALUES = {}
        steps = Step.objects.filter(case_id=case_id).order_by('order')
        if steps.exists():
            for step in steps:
                # print step.name
                # step_name = step.name
                # url = Template.objects.filter(name=step_name).first().url
                # print url
                print '开始执行测试步骤：', step.name
                template = step.template
                if template:
                    url = template.url
                    method = template.method
                    t_data_str = template.data
                    s_data = step.data
                    s_header = step.headers
                    s_check = step.check
                    if s_header:
                        headers = {}
                        for h in s_header.split('&'):
                            key = h.split('=')[0]
                            value = h.split('=')[1]
                            if value.startswith('{{'):
                                value = VALUES.get(value[2:-2], None)
                            headers[key] = value

                            if s_data and t_data_str:
                                t_data = t_data_str.split('&')
                                data = {}
                                for d in s_data.split('&'):
                                    key = d.split('=')[0]
                                    value = d.split('=')[1]
                                    if value.startswith('{{'):
                                        value = VALUES.get(value[2:-2], None)
                                    data[key] = value
                                    if key == 'password':
                                        r_str = ''.join(random.sample(string.ascii_letters + string.digits, 3))
                                        data[key] = base64.encodestring(r_str + value)
                                # 如果步骤中没有指定必填项，赋于模板中维护的默认值
                                for p in t_data:
                                    if p.split('=')[0] != 'sign' and p.split('=')[0] not in data.keys():
                                        data[p.split('=')[0]] = p.split('=')[1]
                            client = http.client(url=url, method=method, headers=headers, data=data)
                            if 'sign' in t_data.split('&'):
                                client.add_sign()
                            client.send()
                            # 添加检查点
                            if s_check:
                                check_list = json.loads(s_check).get("checks", None)
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
    suite = unittest.defaultTestLoader.discover('./', pattern='run.py')
    unittest.TextTestRunner().run(suite)
    # stream = open('./report.html', 'wb')
    # HTMLTestRunnerCN.HTMLTestRunner(stream=stream).run(suite)