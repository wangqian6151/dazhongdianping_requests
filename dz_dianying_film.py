import random
import time
import json
import requests
from bs4 import BeautifulSoup
import pymongo
from pyquery import PyQuery as pq

from dazhongdianping.share.dz_location import dz_location
from dazhongdianping.share.html_from_url import html_from_url, html_from_url_selenium, html_from_uri

db = pymongo.MongoClient()['DianPingFilm']


class Model():
    """
    基类, 用来显示类的信息
    """

    # db = pymongo.MongoClient()['DianPingFilm']

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Film(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = ''
        self.review_num = 0
        self.mean_price = ''
        self.img = ''
        self.type = ''
        self.location = ''
        self.address = ''
        self.lat = ''
        self.lng = ''
        self.precise = 0
        self.confidence = 0
        self.branch = ''
        self.number = ''

    def save(self):
        name = self.__class__.__name__
        print('save', self.__dict__)
        print('mongodb status', db[name].find({"number": self.number}).count())
        if db[name].find({"number": self.number}).count():  # 如果找到number,则只更新
            db[name].update({"number": self.number}, self.__dict__, upsert=True)
        else:  # 如果没有找到number,则插入新的数据
            db[name].save(self.__dict__)

    # def getlocation(self):
    #     address = '深圳' + self.location + self.address
    #     if 'www' in self.address or self.address == '':
    #         address = '深圳' + self.location + self.title
    #     print('enter  getlocation 1: {}'.format(address))
    #     if '，' in address:
    #         address = address.split('，')[0]
    #     if '市中心区' in address:
    #         address = address.replace('市中心区', '福田区')
    #     b = bytes(address, encoding='utf8')
    #     if len(b) > 84:  # 地址最多支持84个字节
    #         # address = bytes.decode(b[:84])
    #         address = address[:28]
    #     print('enter  getlocation 2: {}'.format(address))
    #     url = 'http://api.map.baidu.com/geocoder/v2/'
    #     output = 'json'
    #     ak = '12343454565678787988888888888888'#输入自己的百度ak
    #     uri = url + '?' + 'address=' + address + '&output=' + output + '&ak=' + ak
    #     temp = requests.get(uri)
    #     soup = BeautifulSoup(temp.text, 'lxml')
    #     print(soup.prettify())
    #     my_location = json.loads(soup.find('p').text)
    #     print('my_location: {}'.format(my_location))
    #     if my_location['status'] == 0:  # 服务请求正常召回
    #         self.lat = my_location['result']['location']['lat']  # 纬度
    #         self.lng = my_location['result']['location']['lng']  # 经度
    #     print('lat : {},lng : {}'.format(self.lat, self.lng))
    #     print('{},{}'.format(self.lat, self.lng))

    def address_of_location(self):
        location = self.location
        if '市中心区' in self.location:
            location = self.location.replace('市中心区', '福田区')
        elif '中心区' in self.location:
            location = self.location.replace('中心区', '区')
        address = '深圳' + location + self.address
        if 'www' in self.address or self.address == '':
            address = '深圳' + location + self.title
        print('address_of_location 1: {}'.format(address))
        if '，' in address:
            address = address.split('，')[0]
        b = bytes(address, encoding='utf8')
        if len(b) > 84:  # 地址最多支持84个字节
            # address = bytes.decode(b[:84])
            address = address[:28]
        print('address_of_location 2: {}'.format(address))
        return address

    def getlocation(self):
        address = self.address_of_location()
        url = 'http://api.map.baidu.com/geocoder/v2/'
        output = 'json'
        ak = '12343454565678787988888888888888'#输入自己的百度ak
        uri = url + '?' + 'address=' + address + '&output=' + output + '&ak=' + ak
        temp = html_from_uri(uri)
        soup = BeautifulSoup(temp, 'lxml')
        print(soup.prettify())
        my_location = json.loads(soup.find('p').text)
        print('my_location: {}'.format(my_location))
        if my_location['status'] == 0:  # 服务请求正常召回
            self.lat = my_location['result']['location']['lat']  # 纬度
            self.lng = my_location['result']['location']['lng']  # 经度
            self.precise = my_location['result']['precise']
            # 位置的附加信息，是否精确查找。1为精确查找，即准确打点；0为不精确，即模糊打点（模糊打点无法保证准确度，不建议使用）。
            self.confidence = my_location['result']['confidence']
            # 可信度，描述打点准确度，大于80表示误差小于100m。该字段仅作参考，返回结果准确度主要参考precise参数。
        print('precise: {},confidence: {},lat: {},lng: {}'.format(self.precise, self.confidence, self.lat, self.lng))
        print('{},{}'.format(self.lat, self.lng))
        print('{},{}'.format(self.lng, self.lat))

    def getaddress(self):
        print('lat : {},lng : {}'.format(self.lat, self.lng))
        print('enter  getaddress: {},{}'.format(self.lat, self.lng))
        url = 'http://api.map.baidu.com/geocoder/v2/'
        output = 'json'
        ak = '12343454565678787988888888888888'#输入自己的百度ak
        uri = url + '?' + 'location=' + str(self.lat) + ',' + str(
            self.lng) + '&output=' + output + '&pois=1' + '&ak=' + ak
        temp = html_from_uri(uri)
        soup = BeautifulSoup(temp, 'lxml')
        print(soup.prettify())
        my_address = json.loads(soup.find('p').text)
        print('my_address: {}'.format(my_address))
        if my_address['status'] == 0:  # 服务请求正常召回
            address = my_address['result']['formatted_address']
            print('address in getaddress:{}'.format(address))

# def get_longitude_latitude():
#     for item in db.Film.find():
#         itemurl = item['url']
#         print('itemurl : {}'.format(itemurl))
#         time.sleep(random.randint(2, 5))
#         html = html_from_url(itemurl)
#         # html = html_from_url_selenium(itemurl)
#         print('html : {}'.format(html))
#         e = pq(html)
#         # if 'window.shop_config={' in e('script').text():
#         print('-------------', e('.footer-container').siblings().eq(0).text())


def film_from_li(li):
    """
    从一个 li 里面获取到电影信息
    """
    time.sleep(random.randint(2, 3))
    e = pq(li)

    # 小作用域变量用单字符
    f = Film()
    f.title = e('.txt').find('.tit').find('a').eq(0).text().strip()
    f.url = e('.txt').find('.tit').find('a').eq(0).attr('href')
    if e('.shop-branch').text():
        f.branch = e('.shop-branch').attr('href')
    f.img = e('img').attr('data-src')
    f.star = e('.sml-rank-stars').attr('title')
    if e('.review-num').text():
        print('review-num : {}'.format(e('.review-num').find('b').text()))
        f.review_num = int(e('.review-num').find('b').text())
    f.mean_price = e('.mean-price').text()
    f.type = e('.tag-addr').find('a').eq(0).text().strip()
    f.location = e('.tag-addr').find('a').eq(1).text().strip()
    f.address = e('.addr').text().strip()
    print('before  getlcation: {}'.format(f.address))
    f.getlocation()
    print('after  getlcation: {}'.format(f.address))
    f.getaddress()
    f.number = f.url.split('/')[-1]
    f.save()
    return f


def film_from_url(url):
    """
    从 url 中解析出页面内所有的商家
    """
    page = html_from_url(url)
    e = pq(page)
    items = e('#shop-all-list').find('li')
    film = [film_from_li(i) for i in items]
    return film


def main():
    filmtype = ['g136', 'g25461', 'g33880', 'g33877', 'g33879', 'g33878', 'g33881', 'g33882']

    area = ['r29', 'r31', 'r30', 'r32', 'r12033', 'r12035', 'r34', 'r33']

    random.shuffle(filmtype)
    random.shuffle(area)

    print('filmtype {}'.format(filmtype))
    print('area {}'.format(area))
    for tp in filmtype:
        for loc in area:
            baseurl = 'http://www.dianping.com/shenzhen/ch25/%s%s' % (tp, loc)
            time.sleep(random.randint(2, 5))
            basepage = html_from_url(baseurl)
            e = pq(basepage)
            maxpage = 0
            if e('.PageLink').text():
                maxpage = int(e('.PageLink:last').attr('data-ga-page'))
                # maxpage = int(e('.PageLink').eq(-1).attr('data-ga-page'))
            elif 0 < e('#shop-all-list li').length <= 15:
                maxpage = 1
            else:
                print('maxpage in else: {}'.format(maxpage))
                continue
            print('maxpage: {}'.format(maxpage))
            for i in range(1, maxpage + 1):
                url = baseurl + 'p' + str(i)
                time.sleep(random.randint(5, 10))
                film = film_from_url(url)
                # print('大众点评电影演出赛事', film)

    # for i in range(1, 33):
    #     url = 'http://www.dianping.com/shenzhen/ch25/p{}'.format(i)
    #     time.sleep(random.randint(3, 5))
    #     film = film_from_url(url)
    #     # print('大众点评电影演出赛事', film)


if __name__ == '__main__':
    main()
