import random
import time
import json
from bs4 import BeautifulSoup
import pymongo
from pyquery import PyQuery as pq
from redis import StrictRedis, ConnectionPool
from dazhongdianping.share.dz_location import dz_location
from dazhongdianping.share.html_from_url import html_from_url, html_from_uri


class Model():
    """
    基类, 用来显示类的信息
    """
    db = pymongo.MongoClient()['DianPingBeauty']

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Beauty(Model):
    """
    存储丽人信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = ''
        self.review_num = 0
        self.mean_price = ''
        self.img = ''
        self.effect = 0
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


def beauty_from_li(li):
    """
    从一个 li 里面获取到丽人信息
    """
    time.sleep(random.randint(3, 5))
    e = pq(li)

    # 小作用域变量用单字符
    f = Beauty()
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
    if e('.comment-list').text():
        f.effect = float(e('.comment-list').find('span').eq(0).find('b').text())
        f.environment = float(e('.comment-list').find('span').eq(1).find('b').text())
        f.service = float(e('.comment-list').find('span').eq(2).find('b').text())
    f.type = e('.tag-addr').find('a').eq(0).text().strip()
    f.location = e('.tag-addr').find('a').eq(1).text().strip()
    f.address = e('.addr').text().strip()
    f.getlocation()
    f.number = f.url.split('/')[-1]
    f.save()
    return f


def beauty_from_url(url):
    """
    从 url 中解析出页面内所有的商家
    """
    # url = 'http://www.dianping.com/shenzhen/ch50/g159r64846p1'
    # url = 'http://www.dianping.com/shenzhen/ch50/g33761r8351p3'
    page = html_from_url(url)
    e = pq(page)
    items = e('#shop-all-list ul > li')
    beauty = []
    for i in items:
        e = pq(i)
        print("before e('.txt>.tit>a:first')('href') : {}".format(e('.txt>.tit>a:first').attr('href')))
        if not e('.txt>.tit>a:first').attr('href'):
            print("after e('.txt>.tit>a:first')('href') : {}".format(e('.txt>.tit>a:first').attr('href')))
            return beauty_from_url(url)
        beauty.append(beauty_from_li(i))
    # beauty = [beauty_from_li(i) for i in items]
    return beauty


def main():
    beautytype = ['g157', 'g158', 'g33761', 'g183', 'g148', 'g149', 'g2898', 'g159', 'g493', 'g2572', 'g123', 'g2790']
    cur_location = ['r29', 'r1949', 'r7475', 'r1560', 'r12322', 'r1556', 'r1951', 'r12321', 'r1559', 'r12225', 'r1557',
                    'r1573', 'r12324', 'r12226', 'r12323', 'r3138', 'r12320', 'r12319', 'r1950']
    random.shuffle(beautytype)
    # random.shuffle(dz_location)

    print('beautytype {}'.format(beautytype))
    print('dz_location {}'.format(dz_location))

    for tp in beautytype:
        # for loc in dz_location:
        for loc in cur_location:
            baseurl = 'http://www.dianping.com/shenzhen/ch50/%s%s' % (tp, loc)
            time.sleep(random.randint(2, 5))
            # pool = ConnectionPool(host='localhost', port=6379, db=0, password='123456')
            # redis = StrictRedis(connection_pool=pool)
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
                beauty = beauty_from_url(url)
                # print('大众点评丽人', beauty)


if __name__ == '__main__':
    main()
