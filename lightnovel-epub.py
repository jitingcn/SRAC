#!/usr/bin/env python
# -*- coding: utf-8 -*-

# lightnovel - lightnovel-epub.py
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
        cookies = json.loads(getpass.getpass("请黏贴轻国cookies或直接回车跳过(输入无回显):"))
    except TypeError or json.decoder.JSONDecodeError:
        cookies = None
    if cookies is None:
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
        driver.find_element_by_name("p").send_keys(str(getpass.getpass("密码:(无回显)")))
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
    with open("threadInfo.json", "w") as f:
        f.write(json.dumps(threadInfo))


def get_download_info():  # TODO 完善 网页分析
    all_links = driver.find_elements_by_xpath('//a')
    info = []
    for x in all_links:
        link = x.get_attribute('href')
        try:
            if 'baidu' and '/s/' in link:
                dl_link = link
                dl_link_description = x.find_element_by_xpath('..').text
                dl_text = dl_link_description if dl_link_description is not None else x.text
                if '密码' or '密碼' or '提取码' in dl_text:
                    code = re.findall("(?!epub)([\w\d]{4})", dl_text)[-1]  # TODO 需要修复 这个地方有bug会导致程序中断
                    info.append({'link': dl_link, 'title': dl_text, 'code': code})
                else:
                    info.append({'link': dl_link, 'title': dl_text})
        except TypeError:
            pass
    return info


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    # options.binary_location = '/Applications/Google Chrome'
    # options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    try:
        login()
        # driver.get("https://www.lightnovel.cn/")
        # time.sleep(2)
        lightBookEPUBForum = driver.find_element_by_xpath('//*[@id="category_3"]/table/tbody/tr[3]/td[2]/p[1]/a[2]')
        baseUrl = lightBookEPUBForum.get_attribute('href')[:-6]
        lightBookEPUBForum.click()
        time.sleep(2)

        threadInfo = []
        add_thread_info()
        lastPage = int(
            re.search("([\d]+)", driver.find_element_by_xpath('//*[@id="fd_page_bottom"]/div/a[10]').text).group(0))
        for i in range(2, lastPage + 1):
            driver.get(baseUrl + "%s%s" % (i, '.html'))
            time.sleep(1.5)
            add_thread_info()

        save_thread_info()
        # search link
        for i in range(len(threadInfo)):
            driver.get(threadInfo[i]['link'])
            time.sleep(1.5)
            download_info = get_download_info()
            if len(download_info) == 0:
                download_info = 'Unknown'
            threadInfo[i]['download'] = download_info

        save_thread_info()
    except Exception as e:
        print(e)
    finally:
        driver.close()
