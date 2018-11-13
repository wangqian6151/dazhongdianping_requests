import random
import time
from random import choice
import requests
from lxml import etree
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import string
import zipfile

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "H3284R82886KX1YD"
proxyPass = "350E9CA792A1B7BB"


def create_proxy_auth_extension(proxy_host, proxy_port,
                                proxy_username, proxy_password,
                                scheme='http', plugin_path=None):
    if plugin_path is None:
        plugin_path = r'D:/{}_{}@http-dyn.abuyun.com_9020.zip'.format(proxy_username, proxy_password)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Abuyun Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
            }
          };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )

    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


def html_from_url_selenium(url):
    proxy_auth_plugin_path = create_proxy_auth_extension(
        proxy_host=proxyHost,
        proxy_port=proxyPort,
        proxy_username=proxyUser,
        proxy_password=proxyPass)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--start-maximized")
    # chrome_options.add_extension(proxy_auth_plugin_path)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    html = driver.page_source
    print('driver.page_source:{}'.format(driver.page_source))
    return html


def cookie_from_url(url):
    proxy_auth_plugin_path = create_proxy_auth_extension(
        proxy_host=proxyHost,
        proxy_port=proxyPort,
        proxy_username=proxyUser,
        proxy_password=proxyPass)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--start-maximized")
    # chrome_options.add_extension(proxy_auth_plugin_path)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    cookies = {}
    for cookie in driver.get_cookies():
        cookies.update({cookie['name']: cookie['value']})
    return cookies


# 把浏览器的cookies字符串转成字典
def cookies2dict(cookies):
    items = cookies.split(';')
    d = {}
    for item in items:
        kv = item.split('=', 1)
        k = kv[0]
        v = kv[1]
        d[k] = v
    return d


def html_prase(url):
    r = requests.get(url).content
    return r


def html_from_url(url):
    """
    从 url 中解析出html页面
    """
    # time.sleep(random.randint(3, 5))
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    # proxy = html_prase('http://123.56.28.190:8000/get/').decode('utf-8')
    # proxies = {"http": "http://{}".format(proxy)}
    cookiestring1 = ''
    cookiestring2 = ''
    cookiestring3 = ''
    cookiestring4 = ''
    cookiestring5 = ''
    cookiestring = [cookiestring1, cookiestring2, cookiestring3, cookiestring4, cookiestring5]
    # cookies = cookie_from_url(url)
    cookies = cookies2dict(choice(cookiestring))
    # cookies = {
    #     'cye': 'shenzhen',
    #     '_lxsdk_cuid': '163dcf4d2f3c8-0183cdb3d20aca-5e4b2519-1fa400-163dcf4d2f3c8',
    #     '_lxsdk': '163dcf4d2f3c8-0183cdb3d20aca-5e4b2519-1fa400-163dcf4d2f3c8',
    #     '_hc.v': '4b138761-b7c0-a8ad-c357-a6dd990451c1.1528420422',
    #     's_ViewType': '10',
    #     'dper': 'd50fddf63641be3022a46f9f1df1beabe8ff3f1f356318f7e5dd53f626a49f090962230e66dbc84f2a5c2de6b00da355eb5869626b35ef2df8fa373fcdbd517fe9b530791129f4743b543553926f3985167f8922c2ed52cf228c65ea9d9ca89b',
    #     'ua': 'wangqian6151',
    #     'ctu': '5b6309d42a05ae4dd213481415b102b41b10ffbde57840e084f7ee09eab0b8cb',
    #     'aburl': '1',
    #     'QRCodeBottomSlide': 'hasShown',
    #     'Hm_lvt_4c4fc10949f0d691f3a2cc4ca5065397': '1528971283',
    #     'cityInfo': '%7B%22cityId%22%3A7%2C%22cityEnName%22%3A%22shenzhen%22%2C%22cityName%22%3A%22%E6%B7%B1%E5%9C%B3%22%7D',
    #     '_lx_utm': 'utm_source%3DBaidu%26utm_medium%3Dorganic',
    #     '__mta': '214923560.1528964249753.1529653923944.1529654000913.72',
    #     'selectLevel': '%7B%22level1%22%3A%222%22%2C%22level2%22%3A%220%22%7D',
    #     'cy': '7',
    #     'll': '7fd06e815b796be3df069dec7836c3df',
    #     'Hm_lvt_dbeeb675516927da776beeb1d9802bd4': '1528420846,1528964229,1529979726',
    #     'cy': '7',
    #     'cityid': '7',
    #     'cye': 'shenzhen',
    #     'wed_user_path': '55|0',
    #     'Hm_lpvt_dbeeb675516927da776beeb1d9802bd4': '1529983552',
    #     '_lxsdk_s': '1643a1d06b1-d16-7b0-dd7%7C%7C338',
    # }
    # cookies = {
    #     'cye': 'shenzhen',
    #     '_lxsdk_cuid': '163dcf4d2f3c8-0183cdb3d20aca-5e4b2519-1fa400-163dcf4d2f3c8',
    #     '_lxsdk': '163dcf4d2f3c8-0183cdb3d20aca-5e4b2519-1fa400-163dcf4d2f3c8',
    #     '_hc.v': '4b138761-b7c0-a8ad-c357-a6dd990451c1.1528420422',
    #     's_ViewType': '10',
    #     'dper': '',
    #     'ua': '',
    #     'ctu': '',
    #     'aburl': '1',
    #     'QRCodeBottomSlide': 'hasShown',
    #     'Hm_lvt_4c4fc10949f0d691f3a2cc4ca5065397': '1528971283,1530176708,1530950732',
    #     'cityInfo': '%7B%22cityId%22%3A7%2C%22cityEnName%22%3A%22shenzhen%22%2C%22cityName%22%3A%22%E6%B7%B1%E5%9C%B3%22%7D',
    #     '__mta': '214923560.1528964249753.1531117013946.1531117019576.120',
    #     'cy': '7',
    #     'll': '',
    #     'Hm_lvt_dbeeb675516927da776beeb1d9802bd4': '1530066838,1530517916,1530588829,1530868655',
    #     'cy': '7',
    #     'cityid': '7',
    #     'cye': 'shenzhen',
    #     'wed_user_path': '1040|0',
    #     'Hm_lpvt_4c4fc10949f0d691f3a2cc4ca5065397': '',
    #     'Hm_lpvt_dbeeb675516927da776beeb1d9802bd4': '',
    #     '_lxsdk_s': '1647d95c767-2be-310-46e%7C%7C140',
    # }
    print("cookies is : {} ".format(cookies))
    ua = UserAgent()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'close',
        'Host': 'www.dianping.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
    }
    print(url)
    print(headers['User-Agent'])
    with requests.Session() as s:
        s.keep_alive = False
        print("2 s.keep_alive:{}".format(s.keep_alive))
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[403, 500, 502, 503, 504])
        s.mount('http://', HTTPAdapter(max_retries=retries))
        s.mount('https://', HTTPAdapter(max_retries=retries))
        # try:
        #     # r = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
        #     # with s.get(url, stream=False, headers=headers, cookies=cookies) as r:
        #     r = s.get(url, stream=False, headers=headers, cookies=cookies)
        # except requests.exceptions.ChunkedEncodingError as e:
        #     # r = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
        #     print('ChunkedEncodingError: {}'.format(e))
        #     return html_from_url(url)
        try:
            with s.get(url, stream=False, headers=headers, cookies=cookies, proxies=proxies) as r:
            # with s.get(url, stream=False, headers=headers, cookies=cookies) as r:
                print('r:{}'.format(r))
                print('r.status_code:{}'.format(r.status_code))
                if not 200 <= r.status_code < 300:
                    print('r.status_code in if:{}'.format(r.status_code))
                    return html_from_url(url)
                print('1 r.encoding:{}'.format(r.encoding))
                encoding = r.encoding
                if encoding in [None, 'ISO-8859-1']:
                    encodings = requests.utils.get_encodings_from_content(r.text)
                    if encodings:
                        encoding = encodings[0]
                    else:
                        encoding = r.apparent_encoding
                    print('2 encoding:{}'.format(encoding))
                    page = r.content.decode(encoding)
                    print('2 encoding page:{}'.format(page))
                else:
                    page = r.text
                    # print('page in else:{}'.format(page))
                selector = etree.HTML(page)
                if selector.xpath('//div[contains(@id, "not-found")]'):
                    print('xpath contains(@id, "not-found"):{}')
                    return html_from_url(url)
                # if url.split('/')[-2] in ['ch55', 'ch90', 'ch70']:
                #     if not selector.xpath('//*[@class="item-rank-rst"]'):
                #         print('xpath *[@class="item-rank-rst]')
                #         return html_from_url2(url)
                # else:
                #     if not selector.xpath('//*[@class="sml-rank-stars"]'):
                #         print('xpath *[@class="sml-rank-stars"]')
                #         return html_from_url2(url)
                r.close()
                return page
        except Exception as e:
            print('Exception: {}'.format(e))
            return html_from_url(url)


def html_from_url2(url):
    """
    从 url 中解析出html页面
    """
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    # proxy = html_prase('http://123.56.28.190:8000/get/').decode('utf-8')
    # proxies = {"http": "http://{}".format(proxy)}
    cookiestring1 = ''
    cookiestring2 = ''
    cookiestring3 = ''
    cookiestring4 = ''
    cookiestring5 = ''
    cookiestring = [cookiestring1, cookiestring2, cookiestring3, cookiestring4, cookiestring5]
    # cookies = cookie_from_url(url)
    cookies = cookies2dict(choice(cookiestring))
    print("cookies is : {} ".format(cookies))
    ua = UserAgent()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'close',
        'Host': 'www.dianping.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
    }
    print(url)
    print(headers['User-Agent'])
    # try:
    #     with requests.get(url, headers=headers, cookies=cookies, proxies=proxies) as r:
    #         # with s.get(url, stream=False, headers=headers, cookies=cookies) as r:
    #         print('r:{}'.format(r))
    #         print('r.status_code:{}'.format(r.status_code))
    #         if not 200 <= r.status_code < 300:
    #             print('r.status_code in if:{}'.format(r.status_code))
    #             return html_from_url(url)
    #         print('1 r.encoding:{}'.format(r.encoding))
    #         encoding = r.encoding
    #         if encoding in [None, 'ISO-8859-1']:
    #             encodings = requests.utils.get_encodings_from_content(r.text)
    #             if encodings:
    #                 encoding = encodings[0]
    #             else:
    #                 encoding = r.apparent_encoding
    #             print('2 encoding:{}'.format(encoding))
    #             page = r.content.decode(encoding)
    #             print('2 encoding page:{}'.format(page))
    #         else:
    #             page = r.text
    #         selector = etree.HTML(page)
    #         if selector.xpath('//div[contains(@id, "not-found")]'):
    #             return html_from_url2(url)
    #         return page
    # except Exception as e:
    #     print('Exception: {}'.format(e))
    #     return html_from_url2(url)
    # with requests.get(url, headers=headers, cookies=cookies, proxies=proxies) as r:
        # with s.get(url, headers=headers, cookies=cookies) as r:
    r = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
    print('r:{}'.format(r))
    print('r.status_code:{}'.format(r.status_code))
    if not 200 <= r.status_code < 300:
        print('r.status_code in if:{}'.format(r.status_code))
        return html_from_url2(url)
    print('1 r.encoding:{}'.format(r.encoding))
    encoding = r.encoding
    if encoding in [None, 'ISO-8859-1']:
        encodings = requests.utils.get_encodings_from_content(r.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = r.apparent_encoding
        print('2 encoding:{}'.format(encoding))
        page = r.content.decode(encoding)
        print('2 encoding page:{}'.format(page))
    else:
        page = r.text
    selector = etree.HTML(page)
    if selector.xpath('//div[contains(@id, "not-found")]'):
        return html_from_url2(url)
    # if url.split('/')[-2] in ['ch55', 'ch90', 'ch70']:
    #     if not selector.xpath('//*[@class="item-rank-rst"]'):
    #         print('xpath *[@class="item-rank-rst]')
    #         return html_from_url2(url)
    # else:
    #     if not selector.xpath('//*[@class="sml-rank-stars"]'):
    #         print('xpath *[@class="sml-rank-stars"]')
    #         return html_from_url2(url)
    r.close()
    return page


def html_from_uri(uri):
    with requests.Session() as s:
        s.keep_alive = False
        # print("uri s.keep_alive:{}".format(s.keep_alive))
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[403, 500, 502, 503, 504])
        s.mount('http://', HTTPAdapter(max_retries=retries))
        s.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            with s.get(uri, stream=False) as r:
                # print('uri r:{}'.format(r))
                # print('uri r.status_code:{}'.format(r.status_code))
                if not 200 <= r.status_code < 300:
                    print('uri r.status_code in if:{}'.format(r.status_code))
                    return html_from_uri(uri)
                # print('uri 1 r.encoding:{}'.format(r.encoding))
                encoding = r.encoding
                if encoding in [None, 'ISO-8859-1']:
                    encodings = requests.utils.get_encodings_from_content(r.text)
                    if encodings:
                        encoding = encodings[0]
                    else:
                        encoding = r.apparent_encoding
                    print('uri 2 encoding:{}'.format(encoding))
                    page = r.content.decode(encoding)
                    print('uri 2 encoding page:{}'.format(page))
                else:
                    page = r.text
                r.close()
                return page
        except Exception as e:
            print('Exception in html_from_uri: {}'.format(e))
            return html_from_uri(uri)
