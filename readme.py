import os
import re
from urllib import request
from urllib.parse import urljoin


article_url = 'https://gitee.com/learn_life/BoKeWenZhang/tree/master/aritcle'
article_head = '''# 博客文章
---{}'''.format(os.linesep)
article_body = '#### [{}]({}){}'


response = request.urlopen(article_url)
page = response.read()
content = page.decode('utf8')

filter_content = re.findall(r'iconfont icon-file.+?href="(.+?)" title="(.+?)"', content, re.S)
links = list(map(lambda x: urljoin('https://gitee.com/', x[0]), filter_content))
title = [t[1] for t in filter_content]

with open(r'README.md', 'w', encoding='utf8') as f:
	f.write(article_head)

	for i in range(len(filter_content)):
		f.write(article_body.format(title[i], links[i], os.linesep))