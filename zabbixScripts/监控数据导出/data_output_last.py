#!/usr/bin/env python2.7
# coding=utf-8
import time
import json
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def post_data(data, keyname=''):
    # based url and required header
    url = "http://192.168.174.133/zabbix/api_jsonrpc.php"
    header = {"Content-Type":"application/json"}
    # create request object
    request = urllib2.Request(url,data)
    for key in header:
       request.add_header(key,header[key])
    # auth and get authid
    try:
       result = urllib2.urlopen(request)
    except Exception as e:
       print "连接API失败，失败原因: ", e 
       sys.exit(1)
    else:
       response = json.loads(result.read())
       result.close()

    res = response.get('result')
    if isinstance(res, list) and keyname != '':
        res = ','.join(map(lambda x: x.get(keyname), res))
    return res


def get_authid():
    # auth user and password
    data = json.dumps(
    {
       "jsonrpc": "2.0",
       "method": "user.login",
       "params": {
       "user": "Admin",
       "password": "zabbix"
    },
    "id": 0
    })

    return post_data(data)


def get_hostgroup(authid, groupname):
    # request json
    data = json.dumps(
    {
       "jsonrpc":"2.0",
       "method":"hostgroup.get",
       "params":{
           "output":["groupid","name"],
           "filter":{
           "name": groupname.split(',')
           }
       },
       "auth":"{}".format(authid), # theauth id is what auth script returns, remeber it is string
       "id":1,
    })

    return post_data(data, 'groupid')


def get_host(authid, groupid):
    data = json.dumps(
    {
       "jsonrpc":"2.0",
       "method":"host.get",
       "params":{
           "output":["hostid","name"],
           "groupids": groupid.split(','),
       },
       "auth":"{}".format(authid), # theauth id is what auth script returns, remeber it is string
       "id":1,
    })
    # return post_data(data, 'hostid')
    return post_data(data)


def get_item(authid, hostid):
    # request json
    data = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemids", "name", "lastclock", "lastvalue"],
                "hostids": hostid.split(','),
                "filter": {
                    "key_": ['system.cpu.util[,user]',  'vm.memory.size[available]']
                }
            },
            "auth": "{}".format(authid),  # theauth id is what auth script returns, remeber it is string
            "id": 1,
        })
    return post_data(data)


def get_item_history(authid, itemid):
    # request json
    data = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": 3,
                "itemids": itemid.split(','),
                "limit": 10
            },
            "auth": "{}".format(authid),  # theauth id is what auth script returns, remeber it is string
            "id": 1,
        })

    return post_data(data,)


def time_covert(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


def create_file(content):
    with open('index.html', 'w') as f:
        f.write(content)

if __name__ == '__main__':

    table_msg = '''
    <tr>
        <td align="center">{}</td>
        <td>{}</td>
        <td>{}</td>
        <td align="center">{}</td>
    </tr>
    '''
    msg = '''
    <html>
    <head>
    <style type="text/css">
    table {{border-collapse:collapse;}}
    th {{background-color:#8BB381;}}
    table,th,td {{border: 1px solid black;}}
    </style>
    </head>
    <title>zabbix监控项数据</title>
    <body>
    <b>zabbix监控项数据</b><br>
    <table>
    <tr>
    <th>主机名</th><th>监控项</th><th>时间</th><th>值</th>
    </tr>
    {}
    </table>
    </body>
    </html>
    '''

    re_item = ['system.cpu.load[percpu,avg1]', 'system.cpu.load[percpu,avg5]']
    string = ''

    authid = get_authid()
    groupDict = get_hostgroup(authid, 'Rabbitmq_Server')
    hostDict = get_host(authid, groupDict)
    for host in hostDict:
        item = get_item(authid, host.get('hostid'))
        for i in item:
            i['lastclock'] = time_covert(int(i.get('lastclock')))
            host.update({'item': i})
            print host
            string = string + table_msg.format(host['name'], host['item']['name'], host['item']['lastclock'], host['item']['lastvalue'])
    create_file(msg.format(string))
    # itemid = get_item(authid, hostid)
    # print get_item_history(authid, itemid)

