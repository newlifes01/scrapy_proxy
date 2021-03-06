# -*- coding: utf-8 -*-
import scrapy
import requests
from proxy_ips.items import ProxyIpsItem
from datetime import datetime
from time import sleep

url = "http://2019.ip138.com/ic.asp"
headers = {
    "User-Agent":"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
}


class IpsSpider(scrapy.Spider):
    name = 'ips'
    allowed_domains = ['xicidaili.com']
    start_urls = (
        'https://www.xicidaili.com/nn/',
    )


    def parse(self, response):
        for page in range(2, 5):
            url_next = "https://www.xicidaili.com/nn/{}/".format(page)
            print(url_next)
            sleep(20) # 休眠20秒,防止封ip
            yield scrapy.Request(url_next, callback=self.parse_response_next)

    def parse_response_next(self,response):

        for tr_line in response.xpath('//*[@id="ip_list"]/tr'):

            ip = tr_line.xpath('td[2]/text()').extract_first()
            port = tr_line.xpath('td[3]/text()').extract_first()
            http = str(ip) + ":" + str(port)
            ret = self.__check_ip(http=http)
            if ret:
                item = ProxyIpsItem()
                item["http"] = http
                item["ip"] = str(ip)
                item["port"] = str(port)
                item["is_active"] = True
                item["check_time"] = datetime.now()

                yield item


    def __check_ip(self,http):
        """
        测试ip可用性
        :param http: ip:port
        :return: None
        """
        proxies = {
            "http": "http://{}".format(http),
            "https": "http://{}".format(http),
        }
        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=5, # 请求超时时间超过5秒,认为该ip用不了
            )
            if int(response.status_code) == 200:
                print(http)
                return True
        except:
            pass

        return False



