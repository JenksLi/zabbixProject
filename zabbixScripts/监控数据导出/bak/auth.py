#!/usr/bin/env python2.7
#coding=utf-8
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
    # res = response.get('result')
    # return res


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

    res = post_data(data=data, keyname='groupid')
    return res


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
    return post_data(data, 'hostid')


def get_item(authid, hostid):
    # request json
    data = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemids", "key_"],
                "hostids": hostid.split(','),
            },
            "auth": "{}".format(authid),  # theauth id is what auth script returns, remeber it is string
            "id": 1,
        })
    return post_data(data, 'itemid')


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


if __name__ == '__main__':
    authid = get_authid()
    groupid = get_hostgroup(authid, 'Linux servers')
    hostid = get_host(authid, groupid)
    itemid = get_item(authid, hostid)
    print get_item_history(authid, itemid)

