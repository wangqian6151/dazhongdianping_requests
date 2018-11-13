import random
import re
import time
import pymongo
from pyquery import PyQuery as pq
import json
from bs4 import BeautifulSoup
from dazhongdianping.share.dz_location import dz_location
from dazhongdianping.share.html_from_url import html_from_url, html_from_uri, html_from_url2


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
    存储酒店信息
    """

    def __init__(self):
        self.title = ''
        self.url = ''
        self.star = 0
        self.review_num = 0
        self.price = ''
        self.location = ''
        self.lat = ''
        self.lng = ''
        self.precise = 0
        self.confidence = 0
        self.walk_distance = ''
        self.is_bookable = ''
        self.pic_array = ''
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


def hotel_from_li(li):
    """
    从一个 li 里面获取到一个酒店信息
    """
    time.sleep(random.randint(3, 5))
    e = pq(li)

    # 小作用域变量用单字符
    f = Hotel()
    f.title = e('.hotel-name').find('a').eq(0).text().strip()
    # print('data-poi:{}'.format(e.attr('data-poi')))
    if e.attr('data-poi'):
        f.number = e.attr('data-poi')
    f.url = 'http://www.dianping.com/shop/' + f.number
    f.price = e('.hotel-remark').find('.price').text().strip()
    if e('.sml-rank-stars').attr('class')[-2:] != 'r0':
        f.star = float(e('.sml-rank-stars').attr('class')[-2:]) / 10
    f.review_num = int(e('.remark').text().strip('()'))
    f.location = e('.place').find('a').text()
    f.getlocation()
    # f.getaddress()
    f.walk_distance = e('.walk-dist').text().lstrip('，').strip()
    f.save()
    return f


def hotel_from_url(url):
    """
    从 url 中解析出页面内所有的商家
    """
    # url = 'http://www.dianping.com/shenzhen/hotel/r12036p4'
    page = html_from_url(url)
    e = pq(page)
    if not e('.hotelshop-list .no-hotel-block').text():
        items = e('.hotelshop-list').children('li')
        hotel = [hotel_from_li(i) for i in items]
        return hotel


def hotel_from_url_json(url):
    page = html_from_url2(url)
    print('hotel_from_url_json page type: {},page: {}'.format(type(page), page))
    e = pq(page)
    if not e('.hotelshop-list'):
        print('hotel_from_url_json enter first if')
        return hotel_from_url_json(url)
    if not e('.hotelshop-list .no-hotel-block').text():
        # result = re.findall(r'"hotelList":\s(.*),"breadCrumb":', page)
        m = re.findall('{"hotelList":(.*),"sortInfo"', page)
        print('hotel_from_url_json m: {}'.format(m))
        if not m:
            print('if not m:    m: {}'.format(m))
            return hotel_from_url_json(url)
        print('hotel_from_url_json m[0]: {}'.format(m[0]))
        result = json.loads(m[0] + '}')
        print('hotel_from_url_json result: {}'.format(result))
        print('hotel_from_url_json result.get records: {}'.format(result.get('records')))
        hotel = []
        for record in result.get('records'):
            time.sleep(random.randint(3, 5))
            print('hotel_from_url_json record: {}'.format(record))
            f = Hotel()
            f.title = record.get('shopName')
            f.url = 'http://www.dianping.com' + record.get('shopUrl')
            f.is_bookable = record.get('isBookable')
            f.location = record.get('regionName')
            f.walk_distance = record.get('distanceText')
            f.price = record.get('price')
            f.star = record.get('star') / 10
            f.review_num = record.get('reviewCount')
            f.number = record.get('id')
            f.pic_array = record.get('picArray')
            f.getlocation()
            f.save()
            hotel.append(f)
        print('hotel_from_url_json hotel: {}'.format(hotel))
        return hotel


def main():
    cur_location = ['r12036', 'r8358', 'r8359']
    hoteltype = ['g171', 'g3024', 'g3022', 'g3020']
    random.shuffle(dz_location)
    random.shuffle(cur_location)
    print('cur_location {}'.format(cur_location))
    print('dz_location {}'.format(dz_location))

    # for tp in hoteltype:
    for loc in dz_location[::-1]:
        # for loc in cur_location:
        #     baseurl = 'http://www.dianping.com/shenzhen/hotel/%s%s' % (tp, loc)
        baseurl = 'http://www.dianping.com/shenzhen/hotel/%s' % loc
        time.sleep(random.randint(2, 5))
        basepage = html_from_url2(baseurl)
        e = pq(basepage)
        maxpage = 0
        if e('.page .next'):
            # maxpage = int(e('.PageLink:last').attr('data-ga-page'))
            maxpage = int(e('.page a').eq(-2).text())
        elif e('.page a').length == 1:
            maxpage = 1
        else:
            print('maxpage in else: {}'.format(maxpage))
            continue
        print('maxpage: {}'.format(maxpage))

        # for i in range(1, maxpage + 1):
        for i in range(maxpage, 0, -1):
            url = baseurl + 'p' + str(i)
            time.sleep(random.randint(5, 10))
            # hotel = hotel_from_url(url)
            hotel = hotel_from_url_json(url)
            # print('大众点评酒店', hotel)


if __name__ == '__main__':
    main()
