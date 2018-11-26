#!/usr/bin/env python
# -*- coding: utf-8 -*-

# lightnovel - lightnovel_epub.py
# Created by JT on 13-Nov-18 10:17.
# Blog: https://blog.jtcat.com/
# 
# author = 'JT <jiting@jtcat.com>'

import os
import re
import time
import json
import getpass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def login():
    try:
        cookies = json.loads(getpass.getpass("请黏贴轻国cookies或直接回车跳过(无回显):"))
        if not cookies:
            cookies = None
    except json.decoder.JSONDecodeError:
        print("无效cookies，使用QQ登录")
        print("建议：请确保cookies格式为紧凑json(在同一行内)")
        cookies = None
    if not cookies:
        driver.get("https://www.lightnovel.cn/")
        time.sleep(2)

        driver.find_element_by_xpath('//*[@id="lsform"]/div/div[2]/p[1]/a').click()
        time.sleep(2)

        driver.switch_to.frame("ptlogin_iframe")
        driver.execute_script('document.getElementById("qlogin").style="display: none;"')
        driver.execute_script('document.getElementsByClassName("authLogin").style="display: none;"')
        driver.execute_script('document.getElementById("web_qr_login").style="display: block;"')
        time.sleep(1)

        driver.find_element_by_name("u").clear()
        driver.find_element_by_name("u").send_keys(str(input("请输入QQ号:")))
        driver.find_element_by_name("p").clear()
        driver.find_element_by_name("p").send_keys(str(getpass.getpass("请输入密码(无回显):")))
        driver.find_element_by_id("login_button").click()
        time.sleep(4)
    else:
        driver.get("https://www.lightnovel.cn/")
        time.sleep(3)
        driver.delete_all_cookies()
        for x in cookies:
            driver.add_cookie(x)
    driver.get("https://www.lightnovel.cn/")
    time.sleep(2)
    if not login_check():
        print('失败')
        driver.quit()
        exit()
    else:
        print('登录成功')


def login_check():
    try:
        status = driver.find_element_by_xpath('//*[@id="lsform"]/div/div[1]/table/tbody/tr[2]/td[3]/button').text
    except Exception as err:
        assert 'Unable to locate element' in str(err)
        status = driver.find_element_by_xpath('//*[@id="um"]/p[1]/a[5]').text
        if status == '退出':
            return True
        else:
            print('发生了意外情况')
            driver.quit()
            exit()
    if status == '登录':
        return False


def format_data(import_data):
    print("格式化数据", end=" -> ")
    print("排序", end=" -> ")
    sorted_data = sorted(import_data, key=lambda x: re.findall('(\d{4,8})', x['link'])[-1], reverse=True)
    formatted_data = []
    print("去重", end=" -> ")
    for item in sorted_data:
        link_id = re.findall('(\d{4,8})', item['link'])[-1]
        if len(formatted_data) == 0:
            formatted_data.append(item)
            continue
        if link_id != re.findall('(\d{4,8})', formatted_data[-1]['link'])[-1]:
            formatted_data.append(item)
        else:
            # index = [re.findall('(\d{4,8})', s['link'])[-1] for s in formatted_data].index(i)
            if len(item) > len(formatted_data[-1]):
                formatted_data.pop()
                formatted_data.append(item)
            else:
                if "download" in formatted_data[-1] and "download" in item:
                    if isinstance(formatted_data[-1]["download"], str) and isinstance(item["download"], list):
                        formatted_data.pop()
                        formatted_data.append(item)
                    elif isinstance(formatted_data[-1]["download"], list) and isinstance(item["download"], list):
                        if len(item["download"]) > len(formatted_data[-1]["download"]):
                            formatted_data.pop()
                            formatted_data.append(item)
    print("格式化完毕")
    return formatted_data


def load_data(import_data=None):
    print("从文件读取现有数据", end=' -> ')
    if import_data:
        tmp = import_data
    else:
        tmp = []
    try:
        with open("lightnovel_epub.json", "r", encoding='utf-8') as f:
            tmp.extend(json.load(f))
        print('备份文件', end=' -> ')
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        with open("lightnovel_epub_%s.json" % timestamp, 'w', encoding='utf-8') as f:
            json.dump(tmp, f, sort_keys=True, indent=4, ensure_ascii=False)
        print('导入完毕', end=' ->- ')
        tmp_formatted = format_data(tmp)
        return tmp_formatted
    except FileNotFoundError:
        print('现有数据不存在，跳过')
        return tmp


def save_data(thread_info):
    thread_info = format_data(thread_info)
    print("写入数据到文件", end=' -> ')
    if thread_info:
        with open("lightnovel_epub.json", "w", encoding='utf-8') as f:
            json.dump(thread_info, f, sort_keys=True, indent=4, ensure_ascii=False)
        print('保存完毕')
    else:
        print('无数据输入')


def find_code(dl_link_description, dl_link):
    post_massage = driver.find_element_by_xpath('//*[starts-with(@id, "postmessage")]')
    post_massage_list = post_massage.text.split("\n")
    for y in post_massage_list:
        if dl_link_description in y:
            code = re.findall("(?!epub)(?!\d+MB)(?!big5)([a-zA-Z0-9]{4})", y)
            if len(code) == 0:
                print("未找到提取码，扩大搜索范围", end=" -> ")
                index = post_massage_list.index(y)
                for z in range(index-1, index+2):
                    try:
                        code = re.findall("(?!epub)(?!\d+MB)(?!big5)([a-zA-Z0-9]{4})", post_massage_list[z])
                    except IndexError:
                        continue
                    if len(code) != 0:
                        code = code[-1]
                        if code in dl_link:
                            print("未找到提取码")
                            return []
                        if code.isnumeric():
                            print('似乎没有提取码', code)
                            return []
                        if code != "howf":
                            print('提取码: ', code)
                            return code
                print("未找到提取码")
                return []
            else:
                code = code[-1]
                if code in dl_link:
                    print('似乎没有提取码', code, "扩大搜索范围", end=" -> ")
                    try:
                        code = re.findall("(?!epub)(?!\d+MB)(?!big5)([a-zA-Z0-9]{4})",
                                          post_massage_list[post_massage_list.index(y)+1])
                    except IndexError:
                        code = []
                    if len(code) != 0:
                        code = code[-1]
                        if code in dl_link:
                            print("未找到提取码")
                            return []
                        if code.isnumeric():
                            print('似乎没有提取码', code)
                            return []
                        if code != "howf":
                            print('提取码: ', code)
                            return code
                    print("未找到提取码")
                    return []
                else:
                    print('提取码: ', code)
                    return code
    return []


def get_thread(thread_info, last_page=None):
    forum_entrance = driver.find_element_by_xpath('//*[@id="category_3"]/table/tbody/tr[3]/td[2]/p[1]/a[2]')
    base_url = forum_entrance.get_attribute('href')[:-6]
    forum_entrance.click()
    time.sleep(2)
    if not last_page:
        last_page = int(
            re.search("([\d]+)", driver.find_element_by_xpath('//*[@id="fd_page_bottom"]/div/a[10]').text).group(0))
    elif last_page <= 1:
        last_page = 1
    time.sleep(1)
    for i in range(1, last_page + 1):
        print('获取第 %s 页信息' % i)
        driver.get(base_url + "%s%s" % (i, '.html'))
        time.sleep(1.2)
        thread_info = add_thread_info(thread_info)
    return thread_info


def add_thread_info(thread_info):
    thread_list = driver.find_elements_by_xpath('//*[contains(@id, "normalthread")]')
    for x in range(len(thread_list)):
        thread = thread_list[x].find_element_by_xpath('./tr/th/a[2]')
        link = str(thread.get_attribute('href'))
        title = thread.text
        add = True if link[32:-8] not in [s['link'][32:-8] for s in thread_info] or len(thread_info) == 0 else False
        if add:
            print("添加", title)
            if '查水线' in title:
                print("检查到查水线，跳过")
                continue
            thread_info.append({'title': title, 'link': link})
    return thread_info


def get_thread_info():
    for i in range(len(data)):
        """
            0: Need to be processed 
            1: Need to get code
            2: Processed
        """
        status = 0
        if "download" not in data[i]:
            status = 0
        else:
            if data[i]["download"] == "Unknown":
                status = 0
            else:
                if len(data[i]["download"]) >= 1:
                    for z in data[i]["download"]:
                        if 'baidu.com' in z["link"] and "code" not in z:
                            status = 1
                            break
                        if "code" in z:
                            status = 2
        if status == 0 or status == 1:
            driver.get(data[i]['link'])
            time.sleep(0.3)
            download_info = get_download_info()
            if len(download_info) == 0:
                print('暂无资源: ', data[i]['title'])
                download_info = 'Unknown'
            data[i]['download'] = download_info
        else:
            print("跳过: ", data[i]["title"])


def get_download_info():
    all_links = driver.find_elements_by_xpath('//a[contains(@href, "baidu.com/s")]')
    info = []
    if len(all_links) >= 1:  # 获取百度云分享
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
        all_attachment = driver.find_elements_by_xpath('//*[contains(@id, "attach")]/a')
        if len(all_attachment) >= 1:
            for x in all_attachment:
                try:
                    assert "下载次数" in x.find_element_by_xpath('./following-sibling::em[1]').text
                    info.append({'link': x.get_attribute('href'), 'title': x.text})
                except NoSuchElementException:
                    pass
        else:
            all_attachment = driver.find_elements_by_xpath('//*[contains(@id, "aid")]')
            if len(all_attachment) >= 1:
                for x in all_attachment:
                    try:
                        if "下载次数" in x.find_element_by_xpath('../following-sibling::p[2]').text and x.text != "":
                            info.append({'link': x.get_attribute('href'), 'title': x.text})
                    except NoSuchElementException:
                        pass
            else:  # TODO 其他网盘获取
                pass
        return info


if __name__ == '__main__':
    work_dir = os.getcwd()
    if os.name == 'nt':
        download_dir = "{}\{}".format(work_dir, "download")
        if not os.path.exists(download_dir):
            print("下载文件夹不存在，创建")
            os.makedirs(download_dir)
    else:  # os.name == 'posix'
        download_dir = "{}/{}".format(work_dir, "download")
        if not os.path.exists(download_dir):
            print("下载文件夹不存在，创建")
            os.makedirs(download_dir)

    options = webdriver.ChromeOptions()

    options.add_argument('--headless')  # 无窗口模式
    options.add_argument('--log-level=2')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument('--start-maximized')  # 最大化窗口
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': download_dir,
             "download.prompt_for_download": False}
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(chrome_options=options)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    command_result = driver.execute("send_command", params)

    # data = []
    data = load_data()  # 加载初始化数据
    try:
        login()
        pages = int(input('请输入要获取信息的页数(全部获取请直接回车): ') or 0) or None
        data = get_thread(data, pages)
        save_data(data)

        get_thread_info()
        save_data(data)
    except Exception as e:
        print(e)
    finally:
        save_data(data)
        driver.quit()
