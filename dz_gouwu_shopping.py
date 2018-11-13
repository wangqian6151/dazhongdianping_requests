import random
import time
import json
import requests
from bs4 import BeautifulSoup
import pymongo
from pyquery import PyQuery as pq
from redis import StrictRedis
from dazhongdianping.share.dz_location import dz_location
from dazhongdianping.share.html_from_url import html_from_url, html_from_uri


class Model():
    """
    基类, 用来显示类的信息
    """
    db = pymongo.MongoClient()['DianPingShopping']

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Shopping(Model):
    """
    存储购物信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = ''
        self.review_num = 0
        self.mean_price = ''
        self.img = ''
        self.quality = 0
        self.environment = 0
        self.service = 0
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
        print('mongodb status', self.db[name].find({"number": self.number}).count())
        if self.db[name].find({"number": self.number}).count():  # 如果找到number,则只更新
            self.db[name].update({"number": self.number}, self.__dict__, upsert=True)
        else:  # 如果没有找到number,则插入新的数据
            self.db[name].save(self.__dict__)

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


def shopping_from_li(li):
    """
    从一个 li 里面获取到一个购物信息
    """
    time.sleep(random.randint(2, 3))
    e = pq(li)

    # 小作用域变量用单字符
    f = Shopping()
    f.title = e('.txt').find('.tit').find('a').eq(0).text().strip()
    f.url = e('.txt').find('.tit').find('a').eq(0).attr('href')
    if e('.shop-branch').text():
        f.branch = e('.shop-branch').attr('href')
    f.img = e('img').attr('data-src')
    f.star = e('.sml-rank-stars').attr('title')
    if e('.review-num').text():
        print('review-num : {}'.format(e('.review-num').find('b').text()))
        f.review_num = int(e('.review-num').find('b').text())
    if e('.mean-price').find('b').text():
        f.mean_price = e('.mean-price').find('b').text().strip('￥')
    else:
        f.mean_price = '-'
    if e('.comment-list').text():
        f.quality = float(e('.comment-list').find('span').eq(0).find('b').text())
        f.environment = float(e('.comment-list').find('span').eq(1).find('b').text())
        f.service = float(e('.comment-list').find('span').eq(2).find('b').text())
    f.type = e('.tag-addr').find('a').eq(0).text().strip()
    f.location = e('.tag-addr').find('a').eq(1).text().strip()
    f.address = e('.addr').text().strip()
    f.getlocation()
    f.number = f.url.split('/')[-1]
    f.save()
    return f


def shopping_from_url(url):
    """
    从 html页面中内解析出所有的商家
    """
    page = html_from_url(url)
    e = pq(page)
    items = e('#shop-all-list').find('li')
    shopping = []
    for i in items:
        e = pq(i)
        print("before e('.txt>.tit>a:first')('href') : {}".format(e('.txt>.tit>a:first').attr('href')))
        if not e('.txt>.tit>a:first').attr('href'):
            print("after e('.txt>.tit>a:first')('href') : {}".format(e('.txt>.tit>a:first').attr('href')))
            return shopping_from_url(url)
        shopping.append(shopping_from_li(i))
    # shopping = [shopping_from_li(i) for i in items]
    return shopping


def main():
    shoppingtype = ['g120', 'g33943', 'g33944', 'g33906', 'g33905', 'g33904', 'g119', 'g122', 'g121', 'g130', 'g32739',
                    'g187', 'g235', 'g123', 'g128', 'g125', 'g27809', 'g27810', 'g27811', 'g27812', 'g26085', 'g124',
                    'g127', 'g126', 'g6826', 'g32705', 'g6829', 'g6827', 'g32700', 'g6830', 'g34124', 'g129', 'g184',
                    'g33760', 'g33759', 'g2714', 'g26101', 'g33858', 'g2776', 'g32698', 'g34114', 'g131']

    # shoppingtype = ['g120', 'g33943', 'g33944', 'g33906', 'g33905', 'g33904', 'g119', 'g122', 'g121', 'g130', 'g32739',
    #                 'g187', 'g235', 'g123', 'g128', 'g125', 'g26085', 'g124', 'g127', 'g126', 'g34124', 'g129', 'g184',
    #                 'g2714', 'g26101', 'g33858', 'g2776', 'g32698', 'g34114', 'g131']
    cur_location = ['r34', 'r8646', 'r1957', 'r1570', 'r12335', 'r8647', 'r8357', 'r8355', 'r12334', 'r8648', 'r3141',
                    'r70631']

    random.shuffle(shoppingtype)
    random.shuffle(dz_location)
    print('shoppingtype : {}'.format(shoppingtype))
    print('dz_location : {}'.format(dz_location))

    for tp in shoppingtype:
        # for loc in dz_location:
        for loc in cur_location[::-1]:
            baseurl = 'http://www.dianping.com/shenzhen/ch20/%s%s' % (tp, loc)
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
                shopping = shopping_from_url(url)
                # print('大众点评购物', shopping)


if __name__ == '__main__':
    main()
