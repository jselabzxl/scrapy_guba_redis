# -*- coding:utf-8 -*-

"""guba_stock_detail_spider"""

import re
import json
import math
import urllib2
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaPostDetailAllItem
from guba.utils import _default_mongo, HMS2ts

HOST_URL = "http://guba.eastmoney.com/"

class GubaJlSpider(Spider):
    """usage: scrapy crawl cron_jl_guba_spider -a since_idx=1 -a during=9999 --loglevel=INFO --logfile=run_detail.log
    """
    name = 'cron_jl_guba_spider'

    def __init__(self, since_idx, during):
        self.since_idx = int(since_idx)
        self.max_idx = self.since_idx + int(during)

    def start_requests(self):
        urls = self.prepare()

        for url in urls:
            post_id = int(re.search(r',(.*?),d', url).group(1).split(',')[1])
            request = Request(url)
            request.meta['post_id'] = post_id
            yield request

    def parse(self, response):
        resp = response.body
        post_id = response.meta['post_id']
        soup = BeautifulSoup(resp)

        content = soup.find('div', {'class':'stockcodec'}).text
        stock_id = soup.find('span', {'id': 'stockheadercode'}).find('a').text
        releaseTimePara = re.search(r'发表于 (.*?) (.*?) ', str(soup.find('div', {'class': 'zwfbtime'})))
        part1 = releaseTimePara.group(1).decode('utf-8')
        part2 = releaseTimePara.group(2).decode('utf-8')
        releaseTime = part1 + ' ' + part2

        lastReplyTime = None
        zwlitxb_divs = soup.findAll('div', {'class': 'zwlitime'})
        if len(zwlitxb_divs):
            lastReplyTime = re.search(r'发表于 (.*?)<', str(zwlitxb_divs[0])).group(1).decode('utf-8').replace('  ', ' ')

        item_dict = {'stock_id': stock_id, 'post_id': post_id, 'content': content, 'releaseTime': releaseTime, 'lastReplyTime': lastReplyTime}
        item = GubaPostDetailAllItem()
        for key in GubaPostDetailAllItem.RESP_ITER_KEYS:
            item[key] = item_dict[key]

        return item

    def prepare(self):
        urls = []
        count = 1
        with open('./guba/source/20150119.txt') as f:
            for line in f:
                if count < self.since_idx:
                    count += 1
                    continue
                elif count > self.max_idx:
                    break

                urls.append(line.strip())
                count += 1

        log.msg('[url total count]: {url_count}'.format(url_count=len(urls)))

        return urls

