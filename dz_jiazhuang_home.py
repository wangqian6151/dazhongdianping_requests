import random
import time
import json
import requests
from bs4 import BeautifulSoup
import pymongo
from pyquery import PyQuery as pq
from dazhongdianping.share.dz_location import dz_location
from dazhongdianping.share.html_from_url import html_from_url, html_from_uri


class Model():
    """
    基类, 用来显示类的信息
    """
    db = pymongo.MongoClient()['DianPingHome']

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Home(Model):
    """
    存储家装商家信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = 0
        self.review_num = ''
        self.contract_price = ''
        self.type = ''
        self.img = ''
        self.district = ''
        self.location = ''
        self.lat = ''
        self.lng = ''
        self.precise = 0
        self.confidence = 0
        self.design = ''
        self.designer = ''
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
        address = '深圳' + self.district + self.location + self.title
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


def home_from_li(li):
    """
    从一个 li 里面获取到家装商家信息
    """
    time.sleep(random.randint(3, 5))
    e = pq(li)

    # 小作用域变量用单字符
    f = Home()
    f.title = e('.shop-title>h3>a').text().strip()
    f.url = 'https:' + e('.shop-title>h3>a').attr('href')
    if e('.shop-images img').attr('data-src'):
        f.img = 'http:' + e('.shop-images img').attr('data-src')
    else:
        f.img = 'http:' + e('.shop-images img').attr('src')
    if e('.item-rank-rst').attr('class')[-2:] != 'r0':
        f.star = float(e('.item-rank-rst').attr('class')[-2:]) / 10
    f.review_num = e('.user-comment>a').text()
    td = e('.shop-info-text-i>span').length
    print('td : {}'.format(td))
    if td == 4:
        f.type = e('.shop-info-text-i>span:lt(2)').text()
        f.district = e('.shop-info-text-i>span').eq(-2).text()
        f.location = e('.shop-info-text-i>span:last').text()
    elif td == 3:
        f.type = e('.shop-info-text-i>span:first').text()
        f.district = e('.shop-info-text-i>span').eq(-2).text()
        f.location = e('.shop-info-text-i>span:last').text()
    elif td == 2:
        f.type = e('.shop-info-text-i>span:first').text()
        f.district = e('.shop-info-text-i>span:last').text()
    else:
        print('td in else: {}'.format(td))
    f.number = f.url.split('/')[-1]
    f.getlocation()
    f.save()
    return f


def home_from_item(item):
    """
    从一个 item 里面获取到家装(装修设计/家装卖场)商家信息
    """
    time.sleep(random.randint(3, 5))
    e = pq(item)

    # 小作用域变量用单字符
    f = Home()
    f.title = e('.shop-title>h3>a').text().strip()
    f.url = 'https:' + e('.shop-title>h3>a').attr('href')
    if e('.shop-images img').attr('data-src'):
        f.img = 'http:' + e('.shop-images img').attr('data-src')
    else:
        f.img = 'http:' + e('.shop-images img').attr('src')
    if e('.item-rank-rst').attr('class')[-2:] != 'r0':
        f.star = float(e('.item-rank-rst').attr('class')[-2:]) / 10
    f.review_num = e('.shop-info-text-i>a').text()
    f.contract_price = e('.ml-26:first').text()
    f.district = e('.shop-location>span:first').text()
    f.location = e('.shop-location>span:last').text()
    if e('.shop-team').text():
        f.design = e('.shop-team>a:first').text()
        f.designer = e('.shop-team>a:last').text()
    if e('.ml-26').length > 1:
        f.type = e('.ml-26:last').text()
    else:
        f.type = '装修设计'
    f.number = f.url.split('/')[-1]
    f.getlocation()
    f.save()
    return f


def home_from_url_decoration(url):
    """
    从 url 中解析出页面内所有的商家
    """
    page = html_from_url(url)
    e = pq(page)
    # items = e('.shop-list').children('div')
    # home = [home_from_div(i) for i in items if pq(i).attr('class') != 'shop-list-general']
    items = e('.shop-list').children('.shop-list-item')
    home = [home_from_item(i) for i in items]
    return home


def home_from_url(url):
    """
    从 url 中解析出页面内所有的商家
    """
    page = html_from_url(url)
    e = pq(page)
    items = e('.shop-list').children('li')
    home = [home_from_li(i) for i in items]
    return home


def main():
    hometype = ['g32704', 'g25475', 'g33867', 'g33876', 'g34035', 'g6827', 'g6826', 'g32702', 'g32705']
    # area = ['r29', 'r31', 'r30', 'r32', 'r12036', 'r12033', 'r34', 'r33', 'r12035']
    # random.shuffle(hometype)
    # random.shuffle(area)
    print('hometype {}'.format(hometype))
    # print('area {}'.format(area))

    for tp in hometype:
        for loc in dz_location:
            baseurl = 'http://www.dianping.com/shenzhen/ch90/%s%s' % (tp, loc)
            time.sleep(random.randint(2, 5))
            basepage = html_from_url(baseurl)
            e = pq(basepage)
            maxpage = 0
            if e('.pageLink').text():
                maxpage = int(e('.pageLink:last').attr('title'))
                print('maxpage in first if: {}'.format(maxpage))
                # maxpage = int(e('.PageLink').eq(-1).attr('title'))
            elif e('.pages-num>.pages').text() == '':
                maxpage = 1
                print('maxpage in elif: {}'.format(maxpage))
            else:
                print('maxpage in else: {}'.format(maxpage))
                continue
            print('maxpage: {}'.format(maxpage))

            for i in range(1, maxpage + 1):
                url = baseurl + 'p' + str(i)
                time.sleep(random.randint(5, 10))
                if tp in ['g25475', 'g32704']:
                    print('tp in if : {}'.format(tp))
                    home = home_from_url_decoration(url)
                else:
                    print('tp in else : {}'.format(tp))
                    home = home_from_url(url)
                # print('大众点评家装', home)


if __name__ == '__main__':
    main()
