import os
import argparse
import requests
from lxml import etree
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
class GitHub_download:
    def __init__(self,url):
        self.dir_name = url.split('/')[-1]
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)
        self.get_url(url)
    def login(self,url):
        html = requests.get(url,headers=headers)
        if html.status_code == 200:
            return html.text
    def get_url(self,url):
        text = self.login(url)
        dom = etree.HTML(text)
        urls = dom.xpath('//div[@class="js-details-container Details"]/div/div[*]/div[2]/span/a/@href')
        self.urls = ["https://github.com" + url for url in urls if '.' in url.split('/')[-1]]
        self.download()
    def download(self):
        for url in self.urls:
            name = url.split('/')[-1]
            text = self.login(url)
            soup = BeautifulSoup(text,'lxml')
            data = soup.select('table.highlight.tab-size.js-file-line-container tr')
            with open("./"+self.dir_name+"/"+name,'w') as f:
                f.write(''.join([i.text.replace('\n\n','') for i in data]))
            print(name+":下载完成")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="要下载的网页")
    args = parser.parse_args()
    GitHub_download(args.url)
main()