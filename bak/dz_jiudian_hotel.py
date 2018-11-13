import random
import time

import requests
import pymongo
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Model():
    """
    基类, 用来显示类的信息
    """
    db = pymongo.MongoClient()['DianPingHotel']

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Hotel(Model):
    """
    存储美食信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = ''
        self.review_num = 0
        self.price = ''
        self.location = ''
        self.address = ''
        self.number = ''

    def save(self):
        name = self.__class__.__name__
        print('save', self.__dict__)
        print(self.db[name].find({"number": self.number}).count())
        if self.db[name].find({"number": self.number}).count():  # 如果找到number,则只更新
            self.db[name].update({"number": self.number}, self.__dict__, upsert=True)
        else:  # 如果没有找到number,则插入新的数据
            self.db[name].save(self.__dict__)


def hotel_from_li(li):
    """
    从一个 li 里面获取到一个酒店信息
    """
    time.sleep(random.randint(3, 5))
    e = pq(li)

    # 小作用域变量用单字符
    f = Hotel()
    f.title = e('.hotel-name').find('a').eq(0).text().strip()
    f.number = e.attr('data-poi')
    f.url = 'http://www.dianping.com/shop/' + f.number
    f.price = e('.hotel-remark').find('.price').text().strip()
    f.star = float(e('.sml-rank-stars').attr('class')[-2:]) / 10
    f.review_num = e('.remark').text()
    f.location = e('.place').find('a').text()
    f.walk_distance = e('.walk-dist').text().lstrip('，')
    f.save()
    return f


def hotel_from_url(url):
    """
    从 url 中解析出页面内所有的商家
    """
    cookies = {}
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.list-wrapper .hotelshop-list .hotel-block')))
    page = driver.page_source
    print('driver.page_source: {}'.format(driver.page_source))
    for cookie in driver.get_cookies():
        cookies.update({cookie['name']: cookie['value']})
    print("cookies is : {} ".format(cookies))
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.dianping.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
    }
    print(url)
    # r = requests.get(url, headers=headers, cookies=cookies)
    # print('r:{}'.format(r))
    # print('1 r.encoding:{}'.format(r.encoding))
    # encoding = r.encoding
    # if encoding in [None, 'ISO-8859-1']:
    #     encodings = requests.utils.get_encodings_from_content(r.text)
    #     if encodings:
    #         encoding = encodings[0]
    #     else:
    #         encoding = r.apparent_encoding
    # print('2 encoding:{}'.format(encoding))
    # # page = r.content.decode(encoding)
    # page = r.text
    # # print('r.content:{}'.format(page))
    e = pq(page)
    items = e('.hotelshop-list').find('li')
    # 调用 food_from_li
    hotel = [hotel_from_li(i) for i in items]
    return hotel


def main():
    for i in range(1, 51):
        url = 'http://www.dianping.com/shenzhen/hotel/p{}'.format(i)
        time.sleep(random.randint(3, 5))
        hotel = hotel_from_url(url)
        # print('大众点评酒店', hotel)


if __name__ == '__main__':
    main()
