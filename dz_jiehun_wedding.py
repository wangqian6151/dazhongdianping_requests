import random
import time
import json
from bs4 import BeautifulSoup
import pymongo
from pyquery import PyQuery as pq

from dazhongdianping.share.common import httpSpider
from dazhongdianping.share.dz_location import dz_location
from dazhongdianping.share.html_from_url import html_from_url, html_from_uri

db = pymongo.MongoClient()['DianPingWedding']


class Model():
    """
    基类, 用来显示类的信息
    """

    # db = pymongo.MongoClient()['DianPingWedding']

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Wedding(Model):
    """
    存储结婚商家信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = ''
        self.review_num = ''
        self.mean_price = ''
        self.img = ''
        self.location = ''
        self.lat = ''
        self.lng = ''
        self.precise = 0
        self.confidence = 0
        self.product_photos = ''
        self.number = ''

    def save(self):
        name = self.__class__.__name__
        print('save', self.__dict__)
        # print(self.db[name].find({"number": self.number}).count())
        print('mongodb status', db[name].find({"number": self.number}).count())
        if db[name].find({"number": self.number}).count():  # 如果找到number,则只更新
            db[name].update({"number": self.number}, self.__dict__, upsert=True)
        else:  # 如果没有找到number,则插入新的数据
            db[name].save(self.__dict__)

    def address_of_location(self):
        address = '深圳' + self.location + self.title
        print('address_of_location 1: {}'.format(address))
        if '，' in address:
            address = address.split('，')[0]
        if '市中心区' in address:
            address = address.replace('市中心区', '福田区')
        # elif '中心区' in address:
        #     address = address.replace('中心区', '区')
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


def get_address():
    for item in db.Wedding.find():
        item_url = item['url']
        number = item['number']
        print('item url : {}'.format(item_url))
        time.sleep(random.randint(2, 5))
        html = html_from_url(item_url)
        # html = html_from_url_selenium(item_url)
        # html = httpSpider(item_url)
        print('html : {}'.format(html))
        e = pq(html)
        # if 'window.shop_config={' in e('script').text():
        address = ''
        if e('.road-addr').text():
            address = e('.road-addr').text().strip()
        print('address : {}'.format(address))
        db.Wedding.update({"number": number}, {"$set": {"address": address}}, upsert=True)
        # print('-------------', e('.footer-container').siblings().eq(0).text())


def wedding_from_li(li):
    """
    从一个 li 里面获取到结婚商家信息
    """
    time.sleep(random.randint(3, 5))
    e = pq(li)

    # 小作用域变量用单字符
    f = Wedding()
    f.title = e('.shopname').text().strip()
    f.url = 'http:' + e('.shopname').attr('href').split('?')[0]
    if e('.lists-container'):
        f.img = 'http:' + e('.lists-container').find('img').eq(0).attr('src')
    elif e('a').eq(0).find('img').attr('data-lazyload'):
        f.img = 'http:' + e('a').eq(0).find('img').attr('data-lazyload')
    else:
        f.img = 'http:' + e('a').eq(0).find('img').attr('src')
    f.star = e('.item-rank-rst').attr('title')
    f.review_num = e('.remark').find('span').eq(1).find('a').text()
    f.mean_price = e('.price').text()
    f.product_photos = e('.remark').find('span').eq(2).find('a').text()
    f.location = ' '.join(e('.area-list').text().strip().split())
    f.getlocation()
    f.number = f.url.split('/')[-1]
    f.save()
    return f


def wedding_from_url(url):
    """
    从 url 中解析出页面内所有的商家
    """
    page = html_from_url(url)
    e = pq(page)
    items = e('.shop-list').children('li')
    wedding = [wedding_from_li(i) for i in items]
    return wedding


def main():
    # weddingtype = ['g25410', 'g33888', 'g34057', 'g163', 'g6699', 'g6698', 'g162', 'g983', 'g1016', 'g25411', 'g167',
    #                'g1039', 'g27943', 'g34108', 'g191', 'g2814', 'g2816', 'g2818', 'g166', 'g185', 'g6700', 'g164',
    #                'g25412', 'g186', 'g192', 'g6844']

    weddingtype = ['g25410', 'g33888', 'g34057', 'g163', 'g162', 'g167', 'g191', 'g166', 'g185', 'g6700', 'g164',
                   'g25412', 'g186', 'g192', 'g6844']
    area = ['r29', 'r31', 'r30', 'r32', 'r12036', 'r12033', 'r34', 'r33', 'r12035']
    random.shuffle(weddingtype)
    random.shuffle(area)
    print('weddingtype {}'.format(weddingtype))
    print('area {}'.format(area))
    get_address()
    for tp in weddingtype:
        for loc in area:
            baseurl = 'http://www.dianping.com/shenzhen/ch55/%s%s' % (tp, loc)
            time.sleep(random.randint(2, 5))
            basepage = html_from_url(baseurl)
            e = pq(basepage)
            maxpage = 0
            if e('.PageLink').text():
                maxpage = int(e('.PageLink:last').attr('title'))
                # maxpage = int(e('.PageLink').eq(-1).attr('title'))
            elif 0 < e('.shop-list li').length <= 15:
                maxpage = 1
            else:
                print('maxpage in else: {}'.format(maxpage))
                continue
            print('maxpage: {}'.format(maxpage))

            for i in range(1, maxpage + 1):
                url = baseurl + 'p' + str(i)
                time.sleep(random.randint(5, 10))
                wedding = wedding_from_url(url)
                # print('大众点评结婚', wedding)


if __name__ == '__main__':
    main()
