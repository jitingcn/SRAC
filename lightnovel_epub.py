#!/usr/bin/env python
# -*- coding: utf-8 -*-

# lightnovel - lightnovel_epub.py
# Created by JT on 13-Nov-18 10:17.
# Blog: https://blog.jtcat.com/
# 
# author = 'JT <jiting@jtcat.com>'

import re
import time
import json
import getpass
from selenium import webdriver


def login():
    try:
        cookies = json.loads(getpass.getpass("请黏贴轻国cookies或直接回车跳过(无回显):"))
        if not cookies:
            cookies = None
    except json.decoder.JSONDecodeError:
        cookies = None
    if not cookies:
        driver.get("https://www.lightnovel.cn/")
        time.sleep(5)

        driver.find_element_by_xpath('//*[@id="lsform"]/div/div[2]/p[1]/a').click()
        time.sleep(2)

        driver.switch_to.frame("ptlogin_iframe")
        driver.execute_script('document.getElementById("qlogin").style="display: none;"')
        driver.execute_script('document.getElementsByClassName("authLogin").style="display: none;"')
        driver.execute_script('document.getElementById("web_qr_login").style="display: block;"')
        time.sleep(1)

        driver.find_element_by_name("u").clear()
        driver.find_element_by_name("u").send_keys(str(input("QQ号:")))
        driver.find_element_by_name("p").clear()
        driver.find_element_by_name("p").send_keys(str(getpass.getpass("密码(无回显):")))
        driver.find_element_by_id("login_button").click()
        time.sleep(4)
        # login complete
    else:
        driver.get("https://www.lightnovel.cn/")
        time.sleep(4)
        driver.delete_all_cookies()
        for x in cookies:
            driver.add_cookie(x)
        driver.refresh()
        time.sleep(2)


def add_thread_info():
    thread_list = driver.find_elements_by_xpath('//*[contains(@id, "normalthread")]')
    for x in range(len(thread_list)):
        thread = thread_list[x].find_element_by_xpath('./tr/th/a[2]')
        link = str(thread.get_attribute('href'))
        title = thread.text
        add = True if link not in [s['link'] for s in threadInfo] or len(threadInfo) == 0 else False
        if add:
            threadInfo.append({'title': title, 'link': link})


def save_thread_info():
    try:
        print("正在保存...", end=' -> ')
        if threadInfo is not None:
            with open("lightnovel_epub.json", "w", encoding='utf-8') as f:
                json.dump(threadInfo, f, sort_keys=True, indent=4, ensure_ascii=False)
            print('保存完毕')
        else:
            print('无数据输入')
    except NameError:
        print('无数据输入')


def get_download_info():
    all_links = driver.find_elements_by_xpath('//a[contains(@href, "baidu.com/s")]')
    if len(all_links) >= 1:  # 获取百度云分享
        info = []
        for x in all_links:
            print(driver.title[:-30])
            dl_link = x.get_attribute('href')
            print('链接: ', dl_link)
            dl_link_description = x.find_element_by_xpath('..').text \
                if len(x.find_element_by_xpath('..').text) <= 60 else x.text
            dl_text = driver.title[:-30] if x.text == dl_link else dl_link_description
            code = find_code(dl_link_description, dl_link)
            if code:
                info.append({'link': dl_link, 'title': dl_text, 'code': code})
            else:
                info.append({'link': dl_link, 'title': dl_text})
        return info
    else:
        pass  # TODO 论坛附件及其他网盘下载方式
        return []


def find_code(dl_link_description, dl_link):
    post_massage = driver.find_element_by_xpath('//*[starts-with(@id, "postmessage")]')
    post_massage_list = post_massage.text.split("\n")
    for y in post_massage_list:
        if dl_link_description in y:
            code = re.findall("(?!epub)(?!\d+MB)([a-zA-Z0-9]{4})", y)
            if len(code) == 0:
                print("未找到提取码")
                return []
            else:
                code = code[-1]
                if code in dl_link:
                    print('似乎没有提取码', code)
                    return []
                else:
                    print('提取码: ', code)
                    return code
    return []


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    # options.binary_location = '/Applications/Google Chrome'
    options.add_argument('headless')
    options.add_argument('log-level=2')
    # options.add_argument('start-maximized')
    driver = webdriver.Chrome(chrome_options=options)
    try:
        login()
        driver.get("https://www.lightnovel.cn/")
        time.sleep(1)
        lightBookEPUBForum = driver.find_element_by_xpath('//*[@id="category_3"]/table/tbody/tr[3]/td[2]/p[1]/a[2]')
        baseUrl = lightBookEPUBForum.get_attribute('href')[:-6]
        lightBookEPUBForum.click()
        time.sleep(2)
        print('获取第 1 页信息')
        threadInfo = []
        add_thread_info()
        lastPage = int(
            re.search("([\d]+)", driver.find_element_by_xpath('//*[@id="fd_page_bottom"]/div/a[10]').text).group(0))
        time.sleep(1)
        for i in range(2, lastPage + 1):
            print('获取第 %s 页信息' % i)
            driver.get(baseUrl + "%s%s" % (i, '.html'))
            time.sleep(1.2)
            add_thread_info()

        save_thread_info()
        # search link
        for i in range(len(threadInfo)):
            driver.get(threadInfo[i]['link'])
            time.sleep(0.3)
            download_info = get_download_info()
            if len(download_info) == 0:
                download_info = 'Unknown'
            threadInfo[i]['download'] = download_info

        # save_thread_info()
    except Exception as e:
        print(e)
    finally:
        save_thread_info()
        driver.close()
