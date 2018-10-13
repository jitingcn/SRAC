#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mebook_spider - baidupan_dl_via_links.py
# Created by JT on 04-Sep-18 20:54.

import time
from selenium import webdriver
from ast import literal_eval


def baidu_login(name, passwd):
    url = 'https://pan.baidu.com/'
    driver.get(url)
    print('开始登录')
    time.sleep(2)
    chg_field = driver.find_element_by_id('TANGRAM__PSP_4__footerULoginBtn')
    chg_field.click()

    name_field = driver.find_element_by_id('TANGRAM__PSP_4__userName')
    passwd_field = driver.find_element_by_id('TANGRAM__PSP_4__password')
    login_button = driver.find_element_by_id('TANGRAM__PSP_4__submit')

    name_field.send_keys(name)
    passwd_field.send_keys(passwd)
    login_button.click()
    time.sleep(2)
    try:
        driver.find_element_by_id('TANGRAM__37__button_send_mobile')
        get_code_button = driver.find_element_by_id('TANGRAM__37__button_send_mobile')
        code_field = driver.find_element_by_id('TANGRAM__37__input_vcode')
        code_submit_button = driver.find_element_by_id('TANGRAM__37__button_submit')

        get_code_button.click()
        code = input("输入手机验证码:\n")
        code_field.send_keys(code)
        code_submit_button.click()
        time.sleep(2)
    except Exception as e:
        print('不需要手机登录验证或验证错误', e)
    return driver.get_cookies()


def baidupan_resave():
    with open("dl_baidupan.txt", "r", encoding="utf-8") as f:
        for i in f.readlines():
            data = i.strip().split(" ")
            share_link = data[1]
            if len(data) == 3:
                key = data[2]
            else:
                key = ""
            driver.get(share_link)
            time.sleep(3)
            try:
                if '不存在' in driver.title:
                    print("ID", data[0], '链接失效')
                    continue
            except Exception as e:
                print("Error:", e)
                continue
            if key != "":
                pw_field = driver.find_element_by_id('eoX9ze')
                pw_field.send_keys(key)
                submit_button = driver.find_element_by_xpath('//*[@id="qwl4EQ4"]/a')
                submit_button.click()
                time.sleep(3)
                # 开始转存操作
                file_title = driver.find_element_by_xpath('//*[@id="bd-main"]/div/div[1]/div/div[1]/h2').text
                print("ID", data[0], "转存", file_title, end=" -> ")
                select_all_button = driver.find_element_by_xpath('//*[@id="shareqr"]/div[2]/div[2]/div/ul[1]/li[1]/div/span[1]')
                select_all_button.click()
                time.sleep(2)
                resave_button = driver.find_element_by_xpath('//*[@id="shareqr"]/div[2]/div[2]/div/div/div/div[2]/a[1]')
                resave_button.click()
                time.sleep(3)
                if '最近保存路径' in driver.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[3]').text:
                    driver.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[3]/span').click()
                    save_confirm_button = driver.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[4]/a[2]')
                else:
                    save_confirm_button = driver.find_element_by_xpath('//*[@id="fileTreeDialog"]/div[3]/a[2]')
                save_confirm_button.click()
                time.sleep(3)
                try:
                    if "成功" in driver.find_element_by_xpath('/html/body/div[5]/div/span[2]').text:
                        print("成功")
                    else:
                        print('失败')
                except Exception as e:
                    print("失败或未知错误", e)


if __name__ == '__main__':
    try:
        options = webdriver.ChromeOptions()
        # options.binary_location = '/Applications/Google Chrome'
        options.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=options)
        driver.maximize_window()

        driver.get("https://pan.baidu.com/")
        # cookies = literal_eval(input("输入现有的百度网盘 cookies:\n") or "[0]")
        cookies = [0]

        if len(cookies) < 2:
            login_name = input('请输入你的登录账号:\n')
            login_passwd = input('请输入你的登录密码:\n')
            cookies = baidu_login(login_name, login_passwd)
        for c in cookies:
            driver.add_cookie(c)
        driver.refresh()
        # 完成登录操作
        baidupan_resave()
        time.sleep(60)
        driver.close()
    except Exception as err:
        print('主程序错误:', err)
