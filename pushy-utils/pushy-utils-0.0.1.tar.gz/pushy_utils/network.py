import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
}


class ProxyType(object):
    SOCKS5 = 'SOCKS5'
    HTTP = 'HTTP'


def http_get(url, headers=None):
    if not headers:
        headers = HEADERS
    return requests.get(url, headers=headers)


def http_get_with_proxy(url, proxy_type=ProxyType.HTTP, host='127.0.0.1', port=1081):
    proxy_url = '{}:{}'.format(host, port)
    if proxy_type == ProxyType.HTTP:
        proxy = {
            "http": "http://{}".format(proxy_url),
            "https": "https://{}".format(proxy_url)
        }
    elif proxy_type == ProxyType.SOCKS5:
        proxy = {
            "http": "socks5://".format(proxy_url),
            "https": "socks5://{}".format(proxy_url)
        }
    else:
        raise TypeError('The value of type only has two types: socks5 and http, see ProxyType class')
    return requests.get(url, headers=HEADERS, proxies=proxy)


def download(url, path):
    with open(path, 'wb') as f:
        f.write(requests.get(url).content)


if __name__ == '__main__':
    url = 'https://91mjw.com/images/logo.jpg'
    download(url, "C:\\Users\\Pushy\\Desktop\\hello.png")
