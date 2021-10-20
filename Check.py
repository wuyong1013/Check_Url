#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
用途：
    1、校验网站链接有效性
    2、校验网站下载程序版本号及MD5
说明：
    第一步：先请求官网链接，判断官网链接能否正常打开
    第二步：下载官网包，能否正常下载
    第三步：获取下载包的MD5及版本信息
    第四步：最终结论发送到钉钉

Coders:     
    wuyong
"""
import requests
import re
import json
import os
import time
import ssl
import logging
import shutil
import win32api
import hashlib




# 脚本自动向钉钉机器人发送信息
def post_to_dd(content):
    #钉钉器人地址
    url = ''
    HEADERS = {
        "Content-Type": "application/json ;charset=utf-8"
    }
    String_textMsg = {"msgtype": "text", "text": {"content": content}}
    String_textMsg = json.dumps(String_textMsg)
    res = requests.post(url, data=String_textMsg, headers=HEADERS)
    logging.info(res.text)


# 用来接收url，检测url的状态，并返回状态值
# 增加重试次数
def chain_detect(chain_url):
    count = 0
    stat_code = 0
    while(count < 3):
        try:
            stat = requests.get(chain_url)
            stat_code = stat.status_code
        except:
            logging.error("this url is error : %s" % chain_url)
            stat_code = 0
            break
        if stat_code == 200:
            break
        else:
            count = count + 1
    return stat_code

# 用来获取官网推广渠道的url
# url_0：官方-官网正式版下载
def get_url1():
    list_url1 = []
    #地址1
    content_url1 = requests.get('https://XXX').text
    #print(content_url1)
    #地址2
    content_url2 = requests.get('https://XXX').text
    #地址3
    content_url3 = requests.get('https://XXX').text
    #地址4
    content_url4 = requests.get('https://XXX').text
    # 通过正则匹配获取下载包地址
    # 增加try except，防止出现无链接情况，对于不能提取到url的都认为是异常
    try:
        #下载程序
        url_0 = re.findall('<a href="(.+?)" target="_blank" class="banner-l-btn', content_url1)[0]
        print(url_0)
        #下载程序
        url_1 = re.findall('<a href="(.+?)" target="_blank" class="banner-l-btn', content_url2)[1]
        print(url_1)
        #下载程序
        url_2 = re.findall('<a href="(.+?)" target="_blank" class="item-btn"', content_url3)[0]
        print(url_2)
        #下载程序
        url_3 = re.findall('<a href="(.+?)" target="_blank" class="item-btn"', content_url4)[1]
        print(url_3)
    # 对链接进行一下处理，如果头部没有http:则加上
        if "https" not in url_0:
            url_0 = "https:" + url_0
        if "https" not in url_1:
            url_1 = "https:" + url_1
        if "https" not in url_2:
            url_2 = "https:" + url_2
        if "https" not in url_3:
            url_3 = "https:" + url_3
        list_url1.append(url_0 )
        list_url1.append(url_1)
        list_url1.append(url_2)
        list_url1.append(url_3)
    except:
        logging.error("this is an exception message,get url fail")
        # debug模式下输出链接地址
    logging.debug(list_url1)
    return list_url1


# 用来检测链接对应的包版本号
# 具体方式：1、先把链接中的包下载下来，输出版本号，下载器、非下载器
def get_version(url):
    # 获取脚本所在目录
    path_script = os.getcwd()
    # 如果没有download目录，则创建
    path_download = "".join([path_script, "\\", "download"])
    if os.path.exists(path_download):
        # 容错处理，如果有download目录，先删除整个文件夹，再创建空文件夹
        try:
            shutil.rmtree(path_download)
            time.sleep(0.5)
        except:
            pass
        os.mkdir(path_download)
    else:
        os.mkdir(path_download)
    # 下载安装包
    filename = url.split("/")[-1]
    store_path = "".join([path_download, "\\", filename])
    file_data = requests.get(url).content
    with open(store_path, "wb") as handler:
        handler.write(file_data)
    # 获取安装包的版本号
    info = win32api.GetFileVersionInfo(store_path, os.sep)
    ms = info["FileVersionMS"]
    ls = info["FileVersionLS"]
    version = '%d.%d.%d.%d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
    return version


# 下载文件
def download(add, file_name):
    # continue_flag 标记一下信息是否完整，若不完整返回False，不继续往下走
    continue_flag = True
    try:
        f = urllib.request.urlopen(add)
        data = f.read()
        with open(file_name, "wb") as code:
            code.write(data)
        #print(u"下载成功！")
        continue_flag = True
    except:
        #print(u"下载失败！")
        continue_flag = False
    return continue_flag


# 获取文件md5
def get_md5(file_name):
    with open (file_name, 'rb') as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    return file_md5


if __name__ == '__main__':
    url1 = get_url1()
    # 获取当前时间
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 存放检测结果，用于推送到钉钉
    detect_result = time_now + "\n"
    count_url1 = 0
    # 最终结果，若为0则成功，有大于0则失败
    final_result = 0
    # 建立多个数组，用来存放不同渠道下的推广方式
    list_qd_gf = ["下载1","下载2","下载3","下载4"]
    # 检测官网渠道
    for i in url1:
        result = chain_detect(i)
        if result == 200:
            detect_result = detect_result + "官方渠道-%s：成功，版本号为：%s" % (list_qd_gf[count_url1], get_version(i)) + "\n"+ "下载地址为：%s" % i + "\n"
            #final_result = final_result + 1
        else:
            detect_result = detect_result + "官方渠道-%s：失败" % list_qd_gf[count_url1] + "下载地址为：%s" % i + "\n"
            final_result = final_result + 1
        count_url1 = count_url1 + 1
    # 给出最终结论
    if final_result == 0:
        detect_result = detect_result + "\n" + "结论：所有下载地址均正常。" + "\n"
    else:
        detect_result = detect_result + "\n" + "结论：存在无效下载地址，具体见失败明细！" + "\n"
    #print(detect_result)
    logging.info(detect_result)
    post_to_dd(detect_result)