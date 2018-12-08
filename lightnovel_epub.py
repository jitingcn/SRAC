#!/usr/bin/env python3
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
import codecs
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException


def baidu_login():
    try:
        cookies = json.loads(getpass.getpass("Please paste BaiduNetDisk cookies or enter directly (no echo):"))
        if not cookies:
            cookies = None
    except json.decoder.JSONDecodeError:
        print("Invalid cookies, use account login method.")
        cookies = None
    if not cookies:
        url = 'https://pan.baidu.com/'
        driver.get(url)
        print('Start logging in to BaiduNetDisk.')
        print("Please wait for page loading...")
        chg_field = driver.find_element_by_id('TANGRAM__PSP_4__footerULoginBtn')
        chg_field.click()

        name_field = driver.find_element_by_id('TANGRAM__PSP_4__userName')
        passwd_field = driver.find_element_by_id('TANGRAM__PSP_4__password')
        login_button = driver.find_element_by_id('TANGRAM__PSP_4__submit')
        error_field = driver.find_element_by_id("TANGRAM__PSP_4__error")

        name_field.click()
        name_field.send_keys(str(input("Please enter your phone, email or username:")))
        passwd_field.click()
        passwd_field.send_keys(str(getpass.getpass("Please enter your password (no echo):")))
        login_button.click()
        time.sleep(2)
        if "验证码" in error_field.text:
            print("Login failed, need image verification.")
            driver.quit()
            exit()
        if "登录失败" in error_field.text:
            print("Login failed, may require email/phone verification.")
            # time.sleep(2)
            get_code_button = driver.find_element_by_id('TANGRAM__37__button_send_mobile')
            code_field = driver.find_element_by_id('TANGRAM__37__input_vcode')
            code_submit_button = driver.find_element_by_id('TANGRAM__37__button_submit')
            get_code_button.click()
            print("Verification code has been sent.")
            time.sleep(3)
            code_field.send_keys(str(input("Please enter verification code:\n")))
            code_submit_button.click()
            time.sleep(3)
        elif '用户名或密码有误' in error_field.text:
            print("Username or password is incorrect. Sign in with SMS instead.")
            sms_login_button = driver.find_element_by_id('TANGRAM__PSP_4__smsSwitchWrapper')
            sms_login_button.click()
            phone_number_field = driver.find_element_by_id('TANGRAM__PSP_4__userName')
            phone_number_field.send_keys(str(input("Please enter your phone number:")))
            time.sleep(0.2)
            driver.find_element_by_id('TANGRAM__PSP_4__smsTimer').click()
            time.sleep(1)
            sms_error_field = driver.find_element_by_id('TANGRAM__PSP_4__smsError')
            while sms_error_field.text == '手机号码格式不正确':
                print('The phone number you entered is incorrect.')
                phone_number_field.send_keys(str(input("Please enter your phone number:")))
                time.sleep(0.2)
                driver.find_element_by_id('TANGRAM__PSP_4__smsTimer').click()
                time.sleep(1)
            sms_code_field = driver.find_element_by_id('TANGRAM__PSP_4__smsVerifyCode')
            sms_code_field.send_keys(str(input("Please enter verification code:")))
            time.sleep(0.2)
            sms_login_button = driver.find_element_by_id('TANGRAM__PSP_4__smsSubmit')
            sms_login_button.click()
            time.sleep(1)
            while sms_error_field == '动态密码错误':
                sms_code_field.send_keys(str(input("The verification code is incorrect, please re-enter:")))
                time.sleep(0.2)
                sms_login_button = driver.find_element_by_id('TANGRAM__PSP_4__smsSubmit')
                sms_login_button.click()
                time.sleep(1)
            time.sleep(2)

    else:
        driver.get("https://eyun.baidu.com/")
        for x in cookies:
            driver.add_cookie(x)
        driver.refresh()
        driver.get("https://pan.baidu.com/")
        time.sleep(1)
        for x in cookies:
            driver.add_cookie(x)
        driver.refresh()
        time.sleep(2)
    time.sleep(1)
    if driver.title == "百度网盘-全部文件":
        print("Login successful.")
        baidu_prepare()
    else:
        print("Login failed, quit.")
        time.sleep(300)
        driver.quit()
        exit(1)


def baidu_prepare():
    print("Start initialization...")
    # time.sleep(3)
    try:
        driver.find_element_by_xpath('//*[@id="dialog1"]/div[1]/div/span').click()
        print("Skip the announcement.")
        # time.sleep(1)
    except NoSuchElementException:
        pass
    button = driver.find_elements_by_css_selector('em.icon.icon-newfolder')
    for x in button:
        if x.get_attribute('title') == "新建文件夹":
            x.click()
            time.sleep(0.5)
            break
    named_new_folder_field = driver.find_element_by_class_name("GadHyA")
    submit_button = driver.find_element_by_css_selector('em.icon.umogj0D')
    named_new_folder_field.send_keys(timestamp)
    print("A project folder named %s has been created." % timestamp)
    submit_button.click()
    '''
    test_link = 'https://pan.baidu.com/s/1sj0iBLF'
    driver.get(test_link)
    # time.sleep(1)
    save_button = driver.find_element_by_xpath('//*[@id="layoutMain"]/div[1]/div[1]/div/div[2]/div/div/div[2]/a[1]')
    save_button.click()
    # time.sleep(6)
    file_tree = driver.find_elements_by_xpath('//*[@id="fileTreeDialog"]/div[2]/div/ul/li/ul/li')  # [x]/div/span/span
    for x in file_tree:
        if x.find_element_by_xpath('./div/span/span').text == timestamp:
            x.click()
            break
    driver.find_element_by_class_name('g-button-blue-large').click()
    # time.sleep(1)
    save_button.click()
    # time.sleep(1)
    save_path_item = driver.find_element_by_class_name('save-path-item')
    if "最近保存路径" in save_path_item.text and timestamp in save_path_item.text:
        driver.find_element_by_class_name('save-chk-io').click()
        driver.find_element_by_class_name('g-button-blue-large').click()
    # time.sleep(1)
    '''
    print("Initialization completed.")


def pan_save(link, code=None):
    driver.get(link)
    time.sleep(1)
    if "不存在" in driver.title:
        print("链接已失效")
        return False
    if "输入提取码" in driver.title:
        if code:
            try:
                code_field = WebDriverWait(driver, 5) \
                    .until(expected_conditions.visibility_of_element_located((By.ID, "hgejgNaM")))
                submit_button = WebDriverWait(driver, 5) \
                    .until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "span.text")))
                code_field.send_keys(code)
                time.sleep(0.2)
                submit_button.click()
            except TimeoutException:
                logger("元素超时", link)
                driver.save_screenshot("./logs/error-%s.png" %
                                       time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
                return False
        else:
            print("没有提取码")
            return False
    if WebDriverWait(driver, 5).until(expected_conditions.title_contains("免费")):
        try:
            driver.implicitly_wait(0)
            select_all_button = WebDriverWait(driver, 2.6).until(expected_conditions.visibility_of_element_located(
                (By.XPATH, '//*[@id="shareqr"]/div[2]/div[2]/div/ul[1]/li[1]/div/span[1]')))
            select_all_button.click()
            save_button = driver.find_element_by_xpath(
                '//*[@id="bd-main"]/div/div[1]/div/div[2]/div/div/div[2]/a[1]')
            save_button.click()
            driver.implicitly_wait(10)
        except TimeoutException:
            driver.implicitly_wait(10)
            save_button = driver.find_element_by_xpath(
                '//*[@id="layoutMain"]/div[1]/div[1]/div/div[2]/div/div/div[2]/a[1]')
            save_button.click()
        time.sleep(1)
        index = 4
        try:
            save_path_item = driver.find_element_by_class_name('save-path-item')
            if "最近保存路径" in save_path_item.text and timestamp in save_path_item.text:
                driver.find_element_by_class_name('save-chk-io').click()
        except NoSuchElementException:
            file_tree = driver.find_elements_by_xpath('//*[@id="fileTreeDialog"]/div[2]/div/ul/li/ul/li')
            for y in file_tree:
                if y.find_element_by_xpath('./div/span/span').text == timestamp:
                    y.click()
                    break
            index -= 1
        # driver.find_element_by_class_name('g-button-blue-large').click()
        time.sleep(0.4)
        driver.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[%s]/a[2]/span/span' % index).click()
        return True
    return False


def eyun_save(link, code=None):
    # try:
    driver.get(link)
    if code:
        try:
            code_field = WebDriverWait(driver, 5) \
                .until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "input.share-access-code")))
            submit_button = WebDriverWait(driver, 5) \
                .until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "span.text")))
            code_field.send_keys(code)
            submit_button.click()
        except TimeoutException:
            logger("元素超时", link)
            driver.save_screenshot("./logs/error-%s.png" %
                                   time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
            return False
    else:
        pass
        # print("没有提取码")
        # return False
    time.sleep(1)
    save_button = WebDriverWait(driver, 3) \
        .until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "span.text")))
    save_button.click()
    time.sleep(1.1)
    file_tree = driver.find_elements_by_xpath('//*[@id="fileTreeDialog"]/div[2]/div/ul/li/ul/li')
    for y in file_tree:
        if y.find_element_by_xpath('./div/span/span').text == timestamp:
            y.click()
            break
    time.sleep(0.3)
    driver.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[3]/a[2]/span/span').click()
    return True
    # except Exception as err:
    #     print(err)
    #     driver.save_screenshot("EyunError-%s.png" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    #     return False


def lightnovel_login():
    try:
        cookies = json.loads(getpass.getpass("请黏贴轻国cookies或直接回车跳过(无回显):"))
        if not cookies:
            cookies = None
    except json.decoder.JSONDecodeError:
        print("无效cookies，使用QQ登录")
        cookies = None
    if not cookies:
        driver.get("https://www.lightnovel.cn/")
        time.sleep(1)

        driver.find_element_by_xpath('//*[@id="lsform"]/div/div[2]/p[1]/a').click()
        time.sleep(1)

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
        time.sleep(1)
        # driver.delete_all_cookies()
        for x in cookies:
            driver.add_cookie(x)
    driver.get("https://www.lightnovel.cn/")
    time.sleep(2)
    if not login_check():
        print('登录失败')
        driver.quit()
        exit(1)
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
    sorted_data = sorted(import_data, key=lambda x: regex_link_id.findall(x['link'])[-1], reverse=True)
    formatted_data = []
    print("去重", end=" -> ")
    for item in sorted_data:
        link_id = regex_link_id.findall(item['link'])[-1]
        if len(formatted_data) == 0:
            formatted_data.append(item)
            continue
        if link_id != regex_link_id.findall(formatted_data[-1]['link'])[-1]:
            formatted_data.append(item)
        else:
            # index = [regex_link_id.findall(s['link'])[-1] for s in formatted_data].index(i)
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


def backup_data(import_data):
    print('备份文件')
    with open("lightnovel_epub_%s.json" % timestamp, 'w', encoding='utf-8') as f:
        json.dump(import_data, f, sort_keys=True, indent=4, ensure_ascii=False)


def find_code(dl_link_description, dl_link):
    post_massage = driver.find_element_by_xpath('//*[starts-with(@id, "postmessage")]')
    post_massage_list = post_massage.text.split("\n")
    for y in post_massage_list:
        if dl_link_description in y:
            code = regex_find_code.findall(y)
            if len(code) == 0:
                print("未找到提取码，扩大搜索范围", end=" -> ")
                index = post_massage_list.index(y)
                for z in range(index - 1, index + 2):
                    try:
                        code = regex_find_code.findall(post_massage_list[z])
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
                        code = regex_find_code.findall(post_massage_list[post_massage_list.index(y) + 1])
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


def verify_baidu_pan_link(link, code=None):
    try:
        driver.get(link)
        time.sleep(2)
        if "链接不存在" in driver.title:
            print("链接不存在")
            return 'expired'
        elif "页面不存在" in driver.title:
            print("页面不存在")
            return 'expired'
        elif "免费高速下载" in driver.title:
            if code is None:
                print('OK')
                return 'verified'
            else:
                print("不需要提取码")
                return 'no code'
        elif "请输入提取码" in driver.title:
            if code is None:
                return 'need code'
            else:
                time.sleep(2)
                driver.find_element_by_id('hgejgNaM').send_keys(code)
                submit = driver.find_element_by_css_selector('span.text')
                submit.click()
                time.sleep(2)
                if "免费高速下载" in driver.title:
                    return 'verified'
                else:
                    return 'unconfirmed'
        return 'unconfirmed'
    except Exception as err:
        print(err)
        return 'unconfirmed'


def get_thread(thread_info, last_page=None):
    forum_entrance = driver.find_element_by_xpath('//*[@id="category_3"]/table/tbody/tr[3]/td[2]/p[1]/a[2]')
    base_url = forum_entrance.get_attribute('href')[:-6]
    forum_entrance.click()
    time.sleep(2)
    if not last_page:
        last_page = int(
            re.search(r"([\d]+)", driver.find_element_by_xpath('//*[@id="fd_page_bottom"]/div/a[10]').text).group(0))
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
        link_id = regex_link_id.findall(link)[-1]
        add = True if link_id not in [regex_link_id.findall(s['link'])[-1]
                                      for s in thread_info] or len(thread_info) == 0 else False
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
        # if i == 50:
        #    break

        status = 2
        if "download" not in data[i]:
            status = 0
        '''
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
        '''
        if status == 0 or status == 1:
            driver.get(data[i]['link'])
            time.sleep(0.5)
            download_info = get_download_info()
            if len(download_info) == 0:
                print('暂无资源: ', data[i]['title'])
                download_info = 'Unknown'
            else:
                for x in download_info:
                    if "pan.baidu.com" in x["link"]:
                        if "code" in x:
                            result = verify_baidu_pan_link(x["link"], x["code"])
                        else:
                            result = verify_baidu_pan_link(x["link"])
                        if result == 'expired':
                            x["status"] = 'expired'
                        elif result == 'verified':
                            x["status"] = 'verified'
                        elif result == 'need code':
                            x["status"] = 'need code'
                        elif result == 'no code':
                            x["status"] = 'verified'
                            x.pop('code')
                        elif result == 'unconfirmed':
                            x["status"] = 'unconfirmed'
            data[i]['download'] = download_info
        else:
            # print("跳过: ", data[i]["title"])
            pass


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
                    # driver.save_screenshot("error-%s.png" % time.strftime("%Y%m%d%H%M%S", time.localtime()))
                    pass
        else:
            all_attachment = driver.find_elements_by_xpath('//*[contains(@id, "aid")]')
            if len(all_attachment) >= 1:
                for x in all_attachment:
                    try:
                        if "下载次数" in x.find_element_by_xpath('../following-sibling::p[2]').text and x.text != "":
                            info.append({'link': x.get_attribute('href'), 'title': x.text})
                    except NoSuchElementException:
                        # driver.save_screenshot("error-%s.png" % time.strftime("%Y%m%d%H%M%S", time.localtime()))
                        pass
            else:  # TODO 其他网盘获取
                pass
        return info


def save_process(db):
    for i in db[:]:
        try:
            if isinstance(i["download"], list):
                for x in i["download"]:
                    try:
                        status = False
                        if "status" in x:
                            if x["status"] == 'expired':
                                logger("资源链接失效", i["title"], i["link"], x["link"])
                                continue
                        if "eyun.baidu.com" in x["link"]:
                            if "code" in x:
                                status = eyun_save(x["link"], x["code"])
                            else:
                                status = eyun_save(x["link"])
                        if "pan.baidu.com" in x["link"]:
                            if "code" in x:
                                status = pan_save(x["link"], x["code"])
                            else:
                                status = pan_save(x["link"])
                        if "attachment" in x["link"]:
                            status = True
                        if not status:
                            logger("保存失败", i["title"], i["link"], x["link"])
                    except NoSuchElementException as err:
                        driver.save_screenshot("./logs/error-%s.png" %
                                               time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
                        logger("找不到元素", i["title"], i["link"], str(err))
                    except TimeoutException as err:
                        driver.save_screenshot("./logs/error-%s.png" %
                                               time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
                        logger("程序超时", i["title"], i["link"], str(err))
                    except Exception as err:
                        driver.save_screenshot("./logs/error-%s.png" %
                                               time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
                        logger("程序错误", i["title"], i["link"], str(err))
            else:
                logger("无资源信息", i["title"], i["link"])
        except Exception as err:
            logger("错误", str(err))


def logger(level, *massage):
    log_timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
    with open(log_dir + "log-%s.txt" % timestamp, "a", encoding="utf-8") as f:
        f.write("%s %s %s\n" % (log_timestamp, level, " ".join(massage)))


if __name__ == '__main__':
    regex_link_id = re.compile(r"(\d{4,8})")
    regex_find_code = re.compile(r"(?!epub)(?!\d+MB)(?!big5)([a-zA-Z0-9]{4})")
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    # timestamp = '20181201000000'  # 中断后继续
    work_dir = os.getcwd()
    if os.name == 'nt':
        download_dir = "{}\\{}\\".format(work_dir, "download")
        log_dir = "{}\\{}\\".format(work_dir, "logs")
        conf_dir = "{}\\{}\\".format(work_dir, "conf")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            os.makedirs(log_dir)
            os.makedirs(conf_dir)
    else:  # os.name == 'posix'
        download_dir = "{}/{}/".format(work_dir, "download")
        log_dir = "{}/{}/".format(work_dir, "logs")
        conf_dir = "{}/{}/".format(work_dir, "conf")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            os.makedirs(log_dir)
            os.makedirs(conf_dir)

    options = webdriver.ChromeOptions()
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
         '(KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    headless = input("Run Chrome in headless mode?")  # 无窗口模式
    if headless:
        options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=%s' % ua)

    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': download_dir,
             "download.prompt_for_download": False}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(10)

    if headless:  # 无头模式启用下载文档功能
        driver.set_window_size(1920, 1080)
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)
    else:
        driver.maximize_window()

    # data = []
    baidu_login()
    lightnovel_login()
    data = load_data()  # 加载初始化数据
    try:
        pass
        pages = int(input('请输入要获取信息的页数(全部获取请直接回车): ') or 0) or None
        data = get_thread(data, pages)
        save_data(data)

        get_thread_info()
        save_data(data)

        save_process(data)
    except NoSuchElementException:
        driver.save_screenshot("./logs/error-%s.png" %
                               time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    except Exception as e:
        driver.save_screenshot("./logs/error-%s.png" %
                               time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
        print(e)
    finally:
        save_data(data)
        driver.quit()
