### **zabbix邮件告警配置(腾讯企业邮)**

Zabbix中最初内置了一些预定义的通知[发送方式](https://www.zabbix.com/documentation/3.4/manual/config/notifications/media)。[E-mail](https://www.zabbix.com/documentation/3.4/manual/config/notifications/media/email) 通知是其中的一种。

#### **腾讯企业邮箱介绍**

腾讯企业邮箱默认已支持IMAP、POP3/SMTP等协议，同时不支持非SSL登录。

**POP3/SMTP协议**

接收邮件服务器：pop.exmail.qq.com ，使用SSL，端口号995

发送邮件服务器：smtp.exmail.qq.com ，使用SSL，端口号465 

**IMAP协议**

接收邮件服务器：imap.exmail.qq.com ，使用SSL，端口号993

发送邮件服务器：smtp.exmail.qq.com ，使用SSL，端口号465

更多信息参考[腾讯企业邮箱介绍](https://service.exmail.qq.com/cgi-bin/help?subtype=1&&id=28&&no=1000564)。

#### 配置用户信息

创建接收告警的用户组，前往*管理* *→* *用户群组* *→* *创建用户群组*。

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image002.jpg)

创建接收告警的群组，这里命名为alertgroup

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image004.jpg)

**配置权限**，注意：要获得告警信息，群组对主机群组至少要有读的权限。点击**选择**选择主机群组，完成后点击**添加**，点击**更新**保存

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image006.jpg)

创建用户，并添加到altergroup

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image008.jpg)

配置**报警媒介**→**添加**，添加告警媒介

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image010.png)

**类型**选择zabbix预设的Email，输入接收告警人邮箱地址，点击**更新** 

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image012.jpg)

#### 创建告警项

前往*管理（**Administration**）* *→* *媒体类型（**Media types**）*，点击预定义媒体类型列表中的*Email*，以配置E-mail。

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image014.png)

点击Email 按钮（或创建媒体类型），显示配置页面

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image016.png)

设置对应的SMTP服务器、SMTP HELO、STMP电邮(告警发件人邮箱)，邮箱的账号密码等。注意，腾讯企业邮箱使用SSL，且SMTP服务器的端口为465。

#### **创建告警动作**

在创建完成告警项后，想要获得通知，还需要配置**动作（****Actions****）**，前往*配置（**Configuration**）* *→* *动作（**Actions**）*，然后点击*创建动作（**Create action**）*。注意*事件源*应选择*触发器*

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image018.jpg)

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image020.png)

点击“操作”，配置告警的信息内容并配置具体操作

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image022.jpg)

l  **默认操作步骤持续时间**：默认60(1小时)，在告警未恢复情况下告警通知时间间隔，通知的次数与**操作细节**->**步骤**的设置值有关

l  **步骤**：默认值1-1，发生告警只通知一次。若设置为1-0，表示直至告警恢复，每隔一小时(**步骤持续时间**)进行通知一次。

l  **步骤持续时间**：默认为0，表示使用**默认操作步骤持续时间**的设置值

#### **触发告警测试**

![img](D:\Workspace\Zabbix Scripts\zabbixScripts\告警通知\2018年8月30日 -- 邮件告警\assets\clip_image024.png)