#!/bin/python
# coding:utf8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import json
import base64
import re
import time

def get_token(username, key):
    token = base64.b64encode('{}&{}'.format(username, key))
    token = 'Basic {}'.format(token)
    return token

def send_msg(api_url, token, phoneNumber, param):
    api_url = api_url
    headers = {'Accept': 'text/json', 
                'Accept-Language': 'zh-cn', 
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                'Authorization': token
    }
    post_data = {
        "PhoneNumber": phoneNumber,
        "SignName": "XXXX",		# 
        "TemplateCode": "XXXX",
        "TemplateParam": param,
        "MessageType": ''
    }
    r = requests.post(api_url, headers=headers, data=json.dumps(post_data))
    print r.text.encode('utf8')
    print token
    print 'POST_DATA: ', param

if __name__=='__main__':
    phoneNumber = sys.argv[1]                                                       # zabbix传过来的用户参数
    Subject = sys.argv[2]                                                           # zabbix传过来的告警标题参数
    Content = sys.argv[3]                                                           # zabbix传过来的告警内容参数

    alarm_date = time.strftime('%Y-%m-%d')
    alarm_time = time.strftime('%H:%M:%S')
    pattern = r'''告警主机: (.*)
主机IP: (.*)
告警等级: (.*)
当前状态: (.*)
告警信息: (.*)
告警内容: (.*) 值: (.*)
告警时间: (.*)
告警日期: (.*)'''
    try:
        host_name, host_ip, trigger_severity, trigger_status, trigger_name, item_name, item_value, event_time, event_date = \
        re.search(pattern, Content).groups()
        # map(lambda x: x[:17]+'...' if len(x)>=20 else x, re.search(pattern, Content).groups())
    except Exception as e:
        host_name, host_ip, trigger_severity, trigger_status, trigger_name, item_name, item_value, event_time, event_date = \
        [u'未知', u'未知', u'未知', u'未知', u'未知', u'告警内容匹配失败！', u'请到平台查看信息', alarm_time, alarm_date]

    # 配置API接口信息
    api_url = 'API_URL'
    username = 'USERNAME'
    key = 'KEY'

    # 阿里云短信服务限制发送IP, 以逗号分割
    host_ip = host_ip if host_ip == u'未知' else ','.join(host_ip.split('.'))
    param = {
            'HOST_NAME': host_name,
            'HOST_ADDR': host_ip,
            'TRIGGER_SEVERITY': trigger_severity,
            'TRIGGER_STATUS': trigger_status,
            'TRIGGER_NAME': trigger_name,
            'ITEM_NAME': item_name,
            'ITEM_VALUE': item_value,
            'EVENT_TIME': event_time,
            'EVENT_DATE': event_date
    }
    param_json = json.dumps(param, ensure_ascii=False)

    token = get_token(username, key)
    send_msg(api_url, token, phoneNumber, param_json)
