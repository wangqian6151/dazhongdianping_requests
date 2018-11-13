# -*- coding: utf-8 -*-
import urllib.request
from urllib.request import urlopen
from urllib.request import Request
import http.cookiejar
import random
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

head = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
}


def makeMyOpener(head):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener


def httpSpider(url):
    time.sleep(random.randint(3, 5))
    oper = makeMyOpener(head)
    req_timeout = 5
    uop = oper.open(url, timeout=req_timeout)
    data = uop.read()
    html = data.decode()
    return html


def dynamicSpider(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
        'Connection': 'keep-alive'
    }
    cap = DesiredCapabilities.PHANTOMJS.copy()  # 使用copy()防止修改原代码定义dict
    for key, value in headers.items():
        cap['phantomjs.page.customHeaders.{}'.format(key)] = value
    cap["phantomjs.page.settings.loadImages"] = False
    driver = webdriver.PhantomJS(desired_capabilities=cap)
    # executable_path='D:/phantoms/phantomjs-2.1.1-windows/bin/phantomjs.exe')
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html
