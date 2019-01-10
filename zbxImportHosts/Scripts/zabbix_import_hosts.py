# -*- coding: utf-8 -*- 
from pyzabbix import ZabbixAPI
import pprint
import subprocess
import os.path
import os

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

zabbixUrl   = "http://192.168.174.177/zabbix"
zabbixUser  = "Admin"
zabbixPwd   = "zabbix"

#是否添加Macros
MACROS = False

#获取导入的xls文件名
hostFile="hostlist.csv"

# if len(sys.argv) <= 1:
#     print("Error: Please input file")
#     sys.exit()
# else:
#     hostFile=sys.argv[1]

if not os.path.isfile(os.path.join(os.getcwd(), hostFile)) :
    print('file is not exist')
    sys.exit()


#尝试登陆zabbix平台
try:
    zapi = ZabbixAPI(zabbixUrl)
    zapi.login(zabbixUser, zabbixPwd)
except:
    print '\n 登录zabbix平台出现错误'
    sys.exit()

#通过模板名获取模板ID
def get_templateid(template_name):
    template_data = {
        "host": [template_name]
    }
    #print template_data
    result = zapi.template.get(filter=template_data)
    if result:
        return result[0]['templateid']
    else:
        return result

#通过Proxy名称获取ProxyID
def get_proxyid(proxy_name):
    proxy_data = {
        "host": [proxy_name]
    }
    #print template_data
    result = zapi.proxy.get(filter=proxy_data)
    if result:
        return result[0]['proxyid']
    else:
        return result

#检查组名是否已经存在
def check_group(group_name):
    group_data = {
        "name":[group_name]
    }
    return zapi.hostgroup.get(filter=group_data)

#创建组
def create_group(group_name):
    groupid=zapi.hostgroup.create(name=group_name)

#通过组名获取组ID
def get_groupid(group_name):
    group_date = {
        "name":[group_name]
    }
    return str(zapi.hostgroup.get(filter=group_date)[0]['groupid'])

#添加主机
def create_host(host_data):
    data = {
        "name":[host_data['host']]
    }
    
    if zapi.host.get(filter=data):
        print "主机 %s 已经存在" % host_data["host"]
        return False
    else:
        #print host_data
        res = zapi.host.create(host_data)
        if res: 
            #print "hostid is " + res['hostids'][0]
            if MACROS:
                macro = {
                    "hostid": res['hostids'][0],
                    "macro": "{$SNMP_COMMUNITY}",
                    "value": "ht-read"
                }
                zapi.usermacro.create(macro)
            print "添加主机: %s " % (host_data["host"])
            return True
        else:
            print "添加失败: %s " % (host_data["host"])
            return False

#打开xls文件 
def open_excel( file ):
     try:
         data = xlrd.open_workbook(file)
         return data
     except Exception,e:
         print str(e)

#打开CSV文件
def open_csv( file ):
    hostlist = []

    # stdout = subprocess.check_output("file "+file, shell=True)
    # charset = stdout.split(':')[1].strip() 
    # if charset != "UTF-8 Unicode text" and charset != "ASCII text":
    #     print "Warning: file is not UTF-8 Unicode text, please use dos2unix convertion"
    #     sys.exit()

    try:
        for line in open(file):
            t = tuple(line.strip().split(','))
            if line.startswith('#'):
                continue
            hostlist.append(t)
        return hostlist
    except Exception,e:
        print str(e)

#将xls文件内主机导入到list
def get_hosts(file):
    data = open_excel(file)
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    list = []
    for rownum in range(1,nrows):
      #print table.row_values(rownum)[0]
      list.append(table.row_values(rownum)) 
    return list

def main():
    hosts=open_csv(hostFile)
    countTotal=0
    countSucc=0
    countFail=0
    
    #print hosts
    for host in hosts:
        countTotal += 1
        hostName     = host[0].strip()
        visibleName  = host[1].strip()
        hostIp       = host[2].strip()
        groupName    = host[3].strip()
        template     = host[4].strip()
        templateId   = get_templateid(template)
        interfaceType = host[5].strip()
        port = host[6].strip()
        inventoryType = host[7].strip()
        proxyName = host[8].strip()
        proxyId = get_proxyid(proxyName)

        groupid2 = get_groupid('DB PostgreSQL')

        print "creating " + hostName
        #print "templateid = " + templateId
        if  not check_group(groupName) :
            print u'添加主机组: %s' % groupName
            groupid=create_group(groupName)
            #print groupid
        groupId = get_groupid(groupName)
        host_data = {
            "host": hostName,
            "name": visibleName,
            "interfaces": [
              {
                  "type": interfaceType,
                  "main": 1,
                  "useip": 1,
                  "ip": hostIp,
                  "dns": "",
                  "port": port
              }
            ],
            "proxy_hostid": proxyId,
            "groups": [
              {
                  "groupid": groupId
              },
              {
                   "groupid": groupid2
              }
            ],
            "templates": [
              {
                  "templateid": templateId
              }
            ],
            "inventory": {
              "type": inventoryType
            },
        }
        #print "添加主机: %s ,分组: %s ,模板ID: %s" % (visible_name,group,templateid)
        #print host_data
        res = create_host(host_data)
        if res:
            countSucc += 1
        else:
            countFail += 1
    print("\n\n导入主机： %s 主机, 成功导入：%s, 失败导入：%s" % (countTotal,countSucc,countFail))
    

if __name__=="__main__":
    main()
