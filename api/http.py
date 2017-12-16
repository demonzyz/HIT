#coding:utf-8
# import requests
# import jsonpath
# import pymysql.cursors
#
#
# class client:
#
#     def __init__(self, method, url, headers=None, data=None):
#         self.method = method
#         self.url = url
#         self.headers = headers
#         self.data = data
#         self.response = None
#
#     def send(self):
#         if self.method == 1:
#             self.response = requests.request('POST', self.url, headers=self.headers, data=self.data)
#         elif self.method == 0:
#             self.response = requests.request('GET', self.url, headers=self.headers, params=self.data)
#         else:
#             print '只支持以下请求方法类型：POST--1， GET--0'
#
#
#     def response2json(self):
#         try:
#             return self.response.json()
#         except:
#             print '相应报文非标准格式'
#             return None
#
#     def response2text(self):
#         try:
#             return self.response.text
#         except:
#             return None
#
#     def check_status_code(self, code, message):
#         try:
#             status_code = self.\
#                 response.status_code
#         except:
#             status_code = None
#         assert status_code == code, message
#
#     def log_result(self,message):
#         print message
#
#     def check_contains_str(self, context, message):
#         text = self.response2text()
#         if text:
#             assert text.contains(context), '[%s] 实际结果：%s, 预期结果：%s' % (message, text, context)
#         else:
#             assert False, message
#
#     def check_node_text_equal(self, node_path, context, message):
#         result = jsonpath.jsonpath(self.response2json(), node_path)
#         if result:
#             assert result[0] == context, ' 实际结果：%s, 预期结果：%s' % (message, context)
#         else:
#             assert False, ' 实际结果：%s, 预期结果：%s' % (message,  context)
#
#     def check_db(self, node_path, sql, message):
#         config = {
#             'host': '127.0.0.1',
#             'port': 3306,
#             'username': 'root',
#             'password': '123456',
#             'db': 'demo',
#             'charset': 'utf8',
#         }
#         connection = pymysql.connect(**config)
#         cursor = connection.cursor()
#         cursor.execute(sql)
#         actul = cursor.fetchone()
#         result = jsonpath.jsonpath(self.response2json(), node_path)
#         if result:
#             assert result[0] == actul, message
#         else:
#             assert False, message


#coding:utf-8
import requests
import hashlib
import json
import jsonpath
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import pymysql.cursors

class client():

    def __init__(self, url, method, headers=None, data=None):
        self.response = None
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data

    def add_sign(self):
        list = []
        for k, v in self.data.items():
            if k != 'username':
                list.append('%s=%s' % (k, v))
        list.sort()
        token = self.headers.get('token', None)
        random = self.headers.get('random', None)
        if token and random:
            sign_str = '%spara=%s%s' % (token, '&'.join(list), random)
            md5 = hashlib.md5()
            md5.update(sign_str.encode(encoding="utf-8"))
            sign = md5.hexdigest()
            self.data['sign'] = sign
        else:
            print '生成签名失败，token或random为空'

    def send(self):
        if self.method == 1:
            self.response = requests.request('POST', url=self.url, headers=self.headers, data=self.data)
        elif self.method == 0:
            self.response = requests.request('GET', url=self.url, headers=self.headers, params=self.data)
        else:
            print '不支持的http方法类型'

    def response2json(self):
        try:
            json_str = json.dumps(self.response.json())
        except:
            json_str = None
        return json_str

    def __format(self, message, expected, actual):
        return "[%s] 预期结果:%s，实际结果:%s" % (message, expected, actual)

    def __get_value_from_path(self, node_path):
        if self.response:
            object = jsonpath.jsonpath(self.response.json(), node_path)
            if object:
                return object
        return None

    def check_status_code(self, kargs):
        if self.response:
            result = self.response.status_code
            assert result == kargs.get('code', None), self.__format(kargs.get('message', None), kargs.get('code', None), result)
        else:
            assert False, '响应报文为空'

    def check_contains_str(self, kargs):
        result = self.reponse2json()
        assert kargs.get('str', None) in result, self.__format(kargs.get('message', None), kargs.get('str', None), result)

    def check_node_exist(self, kargs):
        result = self.__get_value_from_path(kargs.get('node_path', None))
        assert result != None, self.__format(kargs.get('message', None), kargs.get('node_path', None)+' 存在', result)

    def check_nodeText_equals(self, kargs):
        text = None
        node = self.__get_value_from_path(kargs.get('node_path', None))
        if node:
            text = node[0]
        assert str(text) == str(kargs.get('context', None)), self.__format(kargs.get('message', None), kargs.get('context', None), text)

    def check_nodeText_notequals(self, kargs):
        text = None
        node = self.__get_value_from_path(kargs.get('node_path', None))
        if node:
            text = node[0]
        assert text != kargs.get('context', None), self.__format(kargs.get('message', None), kargs.get('context', None), text)

    def check_nodeText_startswith(self, kargs):
        text = None
        node = self.__get_value_from_path(kargs.get('node_path', None))
        if node:
            text = node[0]
        assert text.startswith(kargs.get('context', None)) == True, self.__format(kargs.get('message', None), kargs.get('context', None), text)

    def check_nodeText_contains(self, kargs):
        text = None
        node = self.__get_value_from_path(kargs.get('node_path', None))
        if node:
            text = node[0]
        assert kargs.get('context', None) in text, self.__format(kargs.get('message', None), kargs.get('context', None), text)

    def check_nodes_count(self, kargs):
        nodes = self.__get_value_from_path(kargs.get('node_path', None))
        if nodes:
            assert len(nodes) == kargs.get('count', None), self.__format(kargs.get('message', None), kargs.get('count', None), len(nodes))
        else:
            assert False, self.__format(kargs.get('message', None), kargs.get('count', None), None)

    def transfer(self, path):
        value = None
        try:
            json_object = self.response.json()
            object = jsonpath.jsonpath(json_object, path)
            if object:
                value = object[0]
        except Exception, e:
            print e.message
        return value

    @classmethod
    def  exctue_sql(cls, sql):
        config = {
            "host":  "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "123456",
            "db": "demo",
            "charset": "utf8"
        }
        try:
            connection = pymysql.connect(**config)
            cursor = connection.cursor()
            cursor.execute(sql)
            return cursor.fetchone()[0]
        except Exception, e:
            return e.message

    def check_db(self, kargs):
        node = self.__get_value_from_path(kargs.get('node_path', None))
        sql = kargs.get('sql', None)
        result = self.exctue_sql(sql)
        message = kargs.get('message', None)
        if node:
            assert node[0] == result, self.__format(message, node, result)
        else:
            assert False, self.__format(kargs.get('message', None), kargs.get('count', None), None)

    def log_result(self,message):
        print message



if __name__ == '__main__':
    # client = client(method=0, url='http://www.baidu.com')
    # client.send()
    # print client.response.text

    # data = {'id':1}
    # client = client(method=0, url='http://127.0.0.1:9000/hit/task/run/', data=data)
    # client.send()
    # print client.response2json()

    # data = {'id':1}
    # client = client(method=0, url='http://www.baidu.com')
    # client.send()
    # print client.response2text()

    # client = client(method=0, url='http://www.baidu.com')
    # client.send()
    # client.check_status_code(200, '请求百度链接有误')
    # client.log_result('成功')

    # client = client(method=0, url='http://127.0.0.1:9000/hit/task/run/?id=1')
    # client.send()
    # json_object = client.response2json()
    # print jsonpath.jsonpath(json_object,'$.error_code')

    # json_object = {
    #                 "event_list": [
    #                     {
    #                         "id": "1",
    #                         "title": "红米新品发布会",
    #                         "status": 1,
    #                     },
    #                     {
    #                         "id": "32",
    #                         "title": "锤子秋季新品发布会",
    #                         "status": 2,
    #                     }
    #                 ],
    #                 "error_code": 0
    #             }
    # print jsonpath.jsonpath(json_object, '$.event_list[0].title')

    # client = client(method=0, url='http://127.0.0.1:9000/hit/task/run/?id=11')
    # client.send()
    # client.check_status_code(200, '响应状态码错误')
    # client.check_node_text_equal('$.error_code', 0, 'error_code不为0')
    # client.log_result('成功')

    client = client(method=0, url='http://127.0.0.1:9000/hit/task/run/?id=1')
    client.send()
    client.check_status_code({'code': 200, 'message': '响应状态码错误'})
    client.check_nodeText_equals({'node_path': '$.error_code', 'context': 0, 'message': 'error_code不为0'})
    client.log_result('成功')
