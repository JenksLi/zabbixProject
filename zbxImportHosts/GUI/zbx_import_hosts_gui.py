# -*- coding: utf-8 -*- 
import xlrd
import os, re
from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename
from pyzabbix import ZabbixAPI


class MainWindow(object):
    tmp_path = os.getenv('temp')
    tmp_file = os.path.join(tmp_path, 'info.txt')

    def __init__(self):
        self.root = Tk()
        self.root.title('Zabbix导入更新主机-V1.0')
        self.root.resizable(False, False)

        self.file = StringVar()
        self.url = StringVar()
        self.user = StringVar()
        self.pwd = StringVar()
        
        Label(self.root, text='用户名  ').grid(row=0, sticky=W)
        Label(self.root, text='密码  ').grid(row=1, sticky=W)
        Label(self.root, text='API URL  ').grid(row=2, sticky=W)   
        Label(self.root, text="主机列表  ").grid(row=3, sticky=W)
        Label(self.root, text='执行输出  ').grid(row=4, sticky=W+N)

        self.e_url = Entry(self.root, width=35, textvariable=self.url)
        self.e_file = Entry(self.root, width=35, textvariable=self.file)
        self.e_user = Entry(self.root, textvariable=self.user)
        self.e_pwd = Entry(self.root, textvariable=self.pwd)
        self.t_log = ScrolledText(self.root, width=40, height=13)
        self.e_pwd['show'] = '*'

        self.e_user.grid(row=0, column=1, sticky=W)
        self.e_pwd.grid(row=1, column=1, sticky=W)
        self.e_url.grid(row=2, column=1, sticky=W)
        self.e_file.grid(row=3, column=1, sticky=W)
        self.t_log.grid(row=4, column=1, columnspan=2, sticky=W+N)

        Button(self.root, text='选择文件', command=self.selectFile).grid(row=3, column=3, sticky=W)
        Button(self.root, text='提交', width=10,  fg='red', command=self.operateHost).grid(row=5, column=3, sticky=S)

        # 读取上次填写的信息
        try:
            with open(self.tmp_file) as f:  
                vars = f.read().split(',')
                self.url.set(vars[0])
                self.file.set(vars[1])
                self.pwd.set(vars[2])
                self.user.set(vars[3])
        except Exception as e:
            pass

        self.root.mainloop()
        
    def selectFile(self):
        file_ = askopenfilename()
        self.file.set(file_)

    def writeRecoed(self, zabbixUrl, hostFile, zabbixPwd, zabbixUser):
        with open(self.tmp_file, 'w') as f:
            f.write(','.join((zabbixUrl, hostFile, zabbixPwd, zabbixUser)))

    def operateHost(self):
        zabbixUrl, hostFile, zabbixPwd, zabbixUser = self.e_url.get(), self.e_file.get(), self.e_pwd.get(), self.e_user.get()
        self.writeRecoed(zabbixUrl, hostFile, zabbixPwd, zabbixUser) 

        def print2text(string):
            self.t_log.insert('insert', "{}\n".format(string))
            self.t_log.update()

        #通过模板名获取模板ID
        def get_templateid(template_name):
            templateList = []
            template_data = {
                "host": template_name
            }
            result = zapi.template.get(filter=template_data)
            for i in range(len(template_name)):
                templateList.append({"templateid": str(result[i]['templateid'])})

            return templateList

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
            newGroup = []

            for gname in group_name:
                if not zapi.hostgroup.get(filter={"name": gname}):
                    groupid=zapi.hostgroup.create(name=gname)
                    newGroup.append(gname)
            return newGroup

        #通过组名获取组ID
        def get_groupid(group_name):
            groupList = []
            group_date = {
                "name": group_name
            }
            group_res = zapi.hostgroup.get(filter=group_date)
            for i in range(len(group_name)):
                groupList.append({"groupid": str(group_res[i]['groupid'])})
            
            return groupList

        #添加主机
        def create_host(host_data):
            data = {
                "host":[host_data['host']]
            }

            newGroups = host_data['groups']
            newTemplates = host_data['templates']
            newInventory = host_data['inventory']
            hostInfo = zapi.host.get(filter=data)

            if hostInfo:
                print2text("主机 {} 已存在, 更新主机信息..".format(host_data["host"]))
                hostid = hostInfo[0]['hostid']
                zapi.host.update({
                        "hostid": str(hostid),
                        "inventory_mode": 0,
                        "templates": newTemplates,
                        "groups": newGroups,
                        "inventory": newInventory
                    })
                return True
            else:
                res = zapi.host.create(host_data)
                if res: 
                    print2text("添加主机: %s " % (host_data["host"]))
                    return True
                else:
                    print2text("添加失败: %s " % (host_data["host"]))
                    return False

        def multiple_item_spilt(string):
            if string.find(';') != -1:
                string = string.strip().split(';')
            return string

        def open_excel(file):
            data = xlrd.open_workbook(file)
            table = data.sheets()[0]
            nrows = table.nrows
            ncols = table.ncols
            excelList = []
            for rownum in range(1,nrows):
                row_val = table.row_values(rownum)
                row_val = [str(i) for i in row_val]
                row_val = list(map(multiple_item_spilt, row_val))
                excelList.append(row_val) 
            return excelList

        def open_csv( file ):
            hostlist = []

            for line in open(file, encoding='utf-8'):
                if line.startswith('#'): continue
                t = tuple(line.strip().split(','))
                l = list(map(multiple_item_spilt, t))
                hostlist.append(l)
            return hostlist

        try:
            zapi = ZabbixAPI(zabbixUrl)
            zapi.login(zabbixUser, zabbixPwd)

            countTotal, countSucc, countFail = 0, 0, 0
            filetype = os.path.splitext(hostFile)[-1]
            if filetype == '.csv':
                hosts = open_csv(hostFile)
            elif filetype in ('.xls', '.xlsx'):
                hosts = open_excel(hostFile)
            else:
                raise FileNotFoundError("文件格式不正确！")

            for host in hosts:
                countTotal += 1
                hostName     = host[0].strip()
                visibleName  = host[1].strip()
                hostIp       = host[2].strip()
                groupName    = host[3]
                if isinstance(groupName, str): groupName = [groupName.strip()]
                template     = host[4]
                if isinstance(template, str): template = [template.strip()]
                templateId   = get_templateid(template)
                proxyName = host[5].strip()   
                contact = host[6].strip()
                hostType = host[7].strip()

                print2text("检测主机 %s..." % hostName)
                newGroup = check_group(groupName)
                if newGroup: print2text('添加主机组: %s' % ','.join(newGroup))
                groupId = get_groupid(groupName)
                host_data = {
                    "host": hostName,
                    "name": visibleName,
                    "interfaces": [
                      {
                          "type": 1,
                          "main": 1,
                          "useip": 1,
                          "ip": hostIp,
                          "dns": "",
                          "port": 10050
                      }
                    ],
                    "groups": groupId,
                    "templates": templateId,
                    "inventory": {
                      "type": hostType,
                      "contact": contact 
                    }
                }
                if proxyName != '': 
                    proxyId = get_proxyid(proxyName)  
                    host_data.update({"proxy_hostid": proxyId})
                res = create_host(host_data)
                if res:
                    countSucc += 1
                else:
                    countFail += 1
            resultStr = '执行结果: 导入主机： {} 主机, 成功导入：{}, 失败导入：{}'.format(countTotal,countSucc,countFail)
            print2text(resultStr)
            messagebox.showinfo('执行结果', resultStr)
        except Exception as e:
            messagebox.showerror("错误", e)

root = MainWindow()