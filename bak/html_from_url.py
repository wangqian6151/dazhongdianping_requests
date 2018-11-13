import requests
from lxml import etree
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import string
import zipfile

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "H7823RH16RZ9FKQD"
proxyPass = "37D2A83D93D9E6F2"


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


def html_from_url(url):
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
    # cookies = cookie_from_url(url)
    cookies = {
        'cye': 'shenzhen',
        '_lxsdk_cuid': '163dcf4d2f3c8-0183cdb3d20aca-5e4b2519-1fa400-163dcf4d2f3c8',
        '_lxsdk': '163dcf4d2f3c8-0183cdb3d20aca-5e4b2519-1fa400-163dcf4d2f3c8',
        '_hc.v': '4b138761-b7c0-a8ad-c357-a6dd990451c1.1528420422',
        's_ViewType': '10',
        'dper': 'd50fddf63641be3022a46f9f1df1beabe8ff3f1f356318f7e5dd53f626a49f090962230e66dbc84f2a5c2de6b00da355eb5869626b35ef2df8fa373fcdbd517fe9b530791129f4743b543553926f3985167f8922c2ed52cf228c65ea9d9ca89b',
        'ua': 'wangqian6151',
        'ctu': '5b6309d42a05ae4dd213481415b102b41b10ffbde57840e084f7ee09eab0b8cb',
        'aburl': '1',
        'QRCodeBottomSlide': 'hasShown',
        'Hm_lvt_4c4fc10949f0d691f3a2cc4ca5065397': '1528971283',
        'cityInfo': '%7B%22cityId%22%3A7%2C%22cityEnName%22%3A%22shenzhen%22%2C%22cityName%22%3A%22%E6%B7%B1%E5%9C%B3%22%7D',
        '_lx_utm': 'utm_source%3DBaidu%26utm_medium%3Dorganic',
        '__mta': '214923560.1528964249753.1529653923944.1529654000913.72',
        'selectLevel': '%7B%22level1%22%3A%222%22%2C%22level2%22%3A%220%22%7D',
        'cy': '7',
        'll': '7fd06e815b796be3df069dec7836c3df',
        'Hm_lvt_dbeeb675516927da776beeb1d9802bd4': '1528420846,1528964229,1529979726',
        'cy': '7',
        'cityid': '7',
        'cye': 'shenzhen',
        'wed_user_path': '55|0',
        'Hm_lpvt_dbeeb675516927da776beeb1d9802bd4': '1529983552',
        '_lxsdk_s': '1643a1d06b1-d16-7b0-dd7%7C%7C338',
    }
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
    try:
        with requests.Session() as s:
        # r = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
            r = s.get(url, headers=headers, cookies=cookies)
    except requests.exceptions.ChunkedEncodingError as e:
        # r = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
        # r = requests.get(url, headers=headers, cookies=cookies)
        print('ChunkedEncodingError: {}'.format(e))
        return html_from_url(url)
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
    # print('r.content:{}'.format(page))
    selector = etree.HTML(page)
    if selector.xpath('//div[contains(@id, "not-found")]'):
        return html_from_url(url)
    r.close()
    return page
