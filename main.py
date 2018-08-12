#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# mebook_spider - main.py
# Created by JT on 11-Aug-18 20:05.
# 
# author = 'JT <jiting@jtcat.com>'

import requests
import random
import json
from lxml import html
from time import sleep

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/68.0.3440.106 Safari/537.36'
}
base_url = 'http://www.shuwu.mobi'
index = requests.get(base_url, headers=headers)
tree = html.fromstring(index.text)
info = tree.xpath('//*[@id="primary"]/div[2]/div/span[1]')  # get total pages number
# total_pages = info[0].text.split(" ")[5]
total_pages = 226  # for test 226 2017.10.26
print("网站主目录总页数%s" % total_pages)

data = {}

# x.replace(' ', '').replace("《", "").replace("》", " ").replace("（作者）", " ").replace("+", " ").split(" ")

try:
    for page_number in range(1, total_pages + 1):
        page = requests.get('%s/page/%s' % (base_url, page_number), headers=headers)
        tree = html.fromstring(page.text)
        for i in range(2 if page_number == 1 else 1, 12 if page_number == 1 else 11):
            print("正在获取第%s页 第%s本书的信息" % (page_number, (i-1) if page_number == 1 else i))
            tag = tree.xpath('//*[@id="primary"]/ul/li[%s]/div[1]/div[1]/a' % i)
            info = tree.xpath('//*[@id="primary"]/ul/li[%s]/div[2]/h2/a' % i)
            page_id = info[0].attrib["href"].replace("http://www.shuwu.mobi/", "").replace(".html", "")
            if tag[0].text == '公告':
                data[page_id] = [
                    {
                        'link': info[0].attrib["href"],
                        'title': info[0].attrib["title"],
                        'tag': [tag[x].text for x in range(len(tag))],
                    }
                ]
            else:
                # pattern = re.compile('\u300a(.+)\u300b(.+)(?:（..）)(.+)')
                print(info[0].attrib["title"])
                try:
                    m = info[0].attrib["title"].replace(' ', '').replace("《", "").replace("》", " ")
                    m = m.replace("（作者）", " ").replace("(作者)", " ").split(" ")
                    data[page_id] = [
                        {
                            'link': info[0].attrib["href"],
                            'title': m[1],
                            'author': m[2],
                            'type': m[3].split('+'),
                            'tag': [tag[x].text for x in range(len(tag))],
                        }
                    ]
                except Exception as e:
                    data[page_id] = [
                        {
                            'link': info[0].attrib["href"],
                            'title': info[0].attrib["title"],
                            'tag': [tag[x].text for x in range(len(tag))],
                        }
                    ]
        sleep(random.uniform(0.3, 1))
except Exception as e:
    print("发生未知错误", e)

for i in data:
    print("正在尝试获取%s号书籍的下载链接" % i)
    try:
        page = requests.get('%s/download.php?id=%s' % (base_url, i), headers=headers)
        tree = html.fromstring(page.text)
        print("正在解析密码")
        key = tree.xpath("/html/body/div[3]/p[6]")
        m = key[0].text.lstrip("网盘密码：").replace("密码：", " ").replace("\xa0\xa0\xa0\xa0\xa0", " ").split(" ")
        print(m)
        key = {}
        for j in range(0, 4, 2):
            key[m[j]] = m[j+1]
        data[i][0]['key'] = key
        print("正在解析下载链接")
        dl_link = {}
        for n in range(1, 10):
            info = tree.xpath('/html/body/div[5]/a[%s]' % n)
            if len(info) == 0:
                break
            if not info[0].text:
                info1 = tree.xpath('/html/body/div[5]/a[%s]/font' % n)
                dl_link[info1[0].text] = info[0].attrib["href"]
            else:
                dl_link[info[0].text] = info[0].attrib["href"]
        data[i][0]["download"] = dl_link
    except Exception as e:
        print("发生未知错误", e)
    sleep(random.uniform(0.3, 1))

print("正在保存数据")
with open("data.json", "w") as f:
    f.write(json.dumps(data))
