# -*- coding:utf-8 -*-

"""使用scrapy_redis的guba_stock_detail_spider"""

import re
import json
import math
import urllib2
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaPostDetailItem
from guba.utils import _default_mongo, HMS2ts
from guba.middlewares import UnknownResponseError
from guba.scrapy_redis.spiders import RedisSpider

HOST_URL = "http://guba.eastmoney.com/"

class GubaStockDetailRedisSpider(RedisSpider):
    """usage: scrapy crawl guba_stock_detail_redis_spider --loglevel=INFO
              爬取股吧中帖子页数据
    """
    name = 'guba_stock_detail_redis_spider'
    redis_key = 'guba_stock_list_redis_spider:items'

    def parse(self, response):
        resp = response.body
        soup = BeautifulSoup(resp)

        try:
            post_id = int(re.search(r'topicid="(.*?)";', str(soup)).group(1))
        except:
            raise UnknownResponseError

        content = soup.find('div', {'class':'stockcodec'}).text
        releaseTimePara = re.search(r'发表于 (.*?) (.*?) ', str(soup.find('div', {'class': 'zwfbtime'})))
        part1 = releaseTimePara.group(1).decode('utf-8')
        part2 = releaseTimePara.group(2).decode('utf-8')
        releaseTime = part1 + ' ' + part2

        lastReplyTime = None
        zwlitxb_divs = soup.findAll('div', {'class': 'zwlitime'})
        if len(zwlitxb_divs):
            lastReplyTime = re.search(r'发表于 (.*?)<', str(zwlitxb_divs[0])).group(1).decode('utf-8').replace('  ', ' ')

        item_dict = {'post_id': post_id, 'content': content, 'releaseTime': releaseTime, 'lastReplyTime': lastReplyTime}
        item = GubaPostDetailItem()
        for key in GubaPostDetailItem.RESP_ITER_KEYS:
            item[key] = item_dict[key]

        return item

