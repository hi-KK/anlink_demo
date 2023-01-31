#/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import json
import re
import html
import threading
import socket
import struct
from urllib.parse import urlparse


def dns_resolver(url):
    '''
    用于多域名的DNS解析获取IP地址
    '''
    try:
        parse = urlparse(url)
        url_new = parse.netloc
        result = socket.getaddrinfo(url_new, None)
        IP = result[0][4][0]
    except Exception as e:
        IP = ''
    return IP

#在线api查询ip归属地，有限制
def get_ip_info(ip):
    try:
        url = f'https://ipaddr.vercel.app/api/{ip}'
        r = requests.get(url).json()
        dict_ip = r["detail"] #运营商
        addr=r["addr"] #地区
        return dict_ip, addr
    except:
      return '[]'


def Find_anLinks(urls):
    headers={
        'User-Agent':'Mozilla/5.0 (compatible;Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)',
        'Referer':'https://www.baidu.com/'
    }
    for url in urls:
        IP=dns_resolver(url)
        IP_base=get_ip_info(IP)
        try:

            r=requests.get(url,headers=headers,timeout=10)

            code=r.status_code#状态码
            res=r.text
            #filter_js_css = re.compile(r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>|<\s*style[^>]*>[^<]*<\s*/\s*style\s*>|</?[^>]+>|[\t\r\n]', re.I|re.S)
            #过滤html、js和css的正则，容易出现漏报
            respose=html.unescape(res)
            #respose=filter_js_css.sub('', respose)

            rules = []#匹配到的标签
            host=True

            for re_rules in re_rules_list:
                r_find=re.findall(r'{}'.format(re_rules),respose,re.S|re.I)
                if r_find !=[]:
                    rules.append(re_rules)
                    host=False
            if host ==False:
                with open("result.txt", "a") as file:
                    file.write('存在暗链|{}|{}|{}|{}|{}\n\n'.format(url,code,IP,IP_base,rules))
                print('{} 存在暗链'.format(url))
            else:
                with open("result.txt", "a") as file:
                    file.write('未检测出暗链|{}|{}|{}|{}|{}\n\n'.format(url,code,IP,IP_base,rules))
                print('{} 未检测出暗链'.format(url))
        except:
            with open("result.txt", "a") as file:
                file.write('无法访问|{}|{}\n\n'.format(url,IP))
            print('{}:{}请求出错'.format(threading.current_thread().name,url))




banner='''                   
    -------------------------------
      多线程批量暗链检测扫描  v1.0
    -------------------------------                                 
'''
print(banner)

thread=5 #线程数

with open('rules.txt', 'r',encoding='utf-8') as s:
    re_rules_list = s.read().split('\n')

with open('url.txt', 'r') as f:
    urls_list = f.read().split('\n')
urls = []
twoList = [[] for i in range(thread)]

for i, e in enumerate(urls_list):
    twoList[i % thread].append(e)
for i in twoList:
    urls.append(i)
print('主线程开始')
thread_list = [threading.Thread(target=Find_anLinks, args=(urls[i],)) for i in range(len(urls))]
for t in thread_list:
    t.start()
for t in thread_list:
    t.join()
print('主线程结束')