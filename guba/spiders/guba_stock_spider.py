# -*- coding:utf-8 -*-

"""guba_stock_spider"""

import re
import json
import urllib2
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaPostItem
from guba.utils import _default_mongo, HMS2ts

HOST_URL = "http://guba.eastmoney.com/"
LIST_URL = HOST_URL + "list,{stock_id},f_{page}.html" # f表示按照发布时间排序
POST_URL = HOST_URL + "news,{stock_id},{post_id}.html"

class GubaStockSpider(Spider):
    """usage: scrapy crawl guba_stock_spider -a begin_date="2014-12-26 00:00:00" -a end_date="2014-12-27 00:00:00" -a since_idx=1 -a max_idx=3 --loglevel=INFO
       遇到end_date的0时时刻即停止
       end_date: 2014-10-10
    """
    name = 'guba_stock_spider'

    def __init__(self, begin_date, end_date, since_idx, max_idx):
        self.stock_type_list = ['沪A', '沪B', '深A', '深B']
        self.begin_ts = HMS2ts(begin_date)
        self.end_ts = HMS2ts(end_date)
        self.since_idx = int(since_idx)
        self.max_idx = int(max_idx)

    def start_requests(self):
        stock_ids = self.prepare()

        for stock_id in stock_ids:
            request = Request(LIST_URL.format(stock_id=stock_id, page=1))
            request.meta['stock_id'] = stock_id
            request.meta['page'] = 1

            yield request

    def parse(self, response):
        results = []
        page = response.meta['page']
        resp = response.body

        soup = BeautifulSoup(resp)
        stock_title = soup.html.head.title
        stock_id = re.search(r'股吧_(.*?)股吧', str(stock_title)).group(1).decode('utf8')
        stock_name = re.search(r'_(.*?)股吧', str(stock_title)).group(1).decode('utf8')

        stoped = False
        if soup.find('div', {'class': 'noarticle'}):
            stoped = True

        for item_soup in soup.findAll('div', {'class':'articleh'}):
            l1_span = item_soup.find("span", {"class": "l1"})
            if l1_span:
                clicks = int(l1_span.string)

            l2_span = item_soup.find("span", {"class": "l2"})
            if l2_span:
                replies = int(l2_span.string)

            isStockholder = False
            isTopic = False
            em_info = None
            l3_span = item_soup.find("span", {"class": "l3"})
            if l3_span:
                em = l3_span.find("em")
                if em:
                    em_info = em.text

                if em_info:
                    if em_info == u'股东':
                        isStockholder = True
                    elif em_info == u'话题':
                        isTopic = True

                # d表示按照时间排序回复
                post_url = HOST_URL + l3_span.find("a").get("href").replace('.html', ',d.html')
                post_id = int(re.search(r'news,.*?,(.*?),', post_url).group(1))

            l4_span = item_soup.find("span", {"class": "l4"})
            if l4_span:
                l4_span_a = l4_span.find("a")

                if l4_span_a:
                    user_name = l4_span_a.string
                    try:
                        user_id = int(l4_span_a.get("data-popper"))
                    except:
                        user_id = int(l4_span_a.get("data-popstock"))
                    user_url = l4_span_a.get("href")
                else:
                    user_name = l4_span.text
                    user_id = None
                    user_url = None

            if not isTopic:
                item_dict = {'post_id': post_id, 'url': post_url, 'stock_id': stock_id, \
                'stock_name': stock_name, 'user_name': user_name, 'user_url': user_url, 'user_id': user_id, \
                'clicks': clicks, 'replies': replies, 'stockholder': isStockholder, 'istopic': isTopic, \
                'em_info': em_info}

                item = GubaPostItem()
                for key in GubaPostItem.LIST_PAGE_KEYS:
                    item[key] = item_dict[key]

                # request = Request(post_url, callback=self.parsePost)
                postsoup = BeautifulSoup(urllib2.urlopen(post_url))

                post_title = postsoup.find('div', {'id': 'zwconttbt'}).text
                content = postsoup.find('div', {'class':'stockcodec'}).text
                releaseTimePara = re.search(r'发表于 (.*?) (.*?) ', str(postsoup.find('div', {'class': 'zwfbtime'})))
                part1 = releaseTimePara.group(1).decode('utf-8')
                part2 = releaseTimePara.group(2).decode('utf-8')
                releaseTime = part1 + ' ' + part2

                if HMS2ts(releaseTime) > self.end_ts and not em_info:
                    continue

                if HMS2ts(releaseTime) < self.begin_ts and not em_info:
                    stoped = True
                    break

                lastReplyTime = None
                zwlitxb_divs = postsoup.findAll('div', {'class': 'zwlitime'})
                if len(zwlitxb_divs):
                    lastReplyTime = re.search(r'发表于 (.*?)<', str(zwlitxb_divs[0])).group(1).decode('utf-8').replace('  ', ' ')

                    # log.msg(lastReplyTime+'TTTTTTTTTT')

                item_dict = {'title': post_title, 'content': content, 'releaseTime': releaseTime, 'lastReplyTime': lastReplyTime}

                for key in GubaPostItem.POST_PAGE_KEYS:
                    item[key] = item_dict[key]

                results.append(item)

        if not stoped:
            page += 1
            request = Request(LIST_URL.format(stock_id=response.meta['stock_id'], page=page))
            request.meta['stock_id'] = response.meta['stock_id']
            request.meta['page'] = page

            results.append(request)

        return results

    def prepare(self):
        """
        db = settings.get('MONGOD_DB', None)
        host = settings.get('MONGOD_HOST', None)
        port = settings.get('MONGOD_PORT', None)
        stock_collection = settings.get('GUBA_STOCK_COLLECTION', None)

        stock_ids = []
        db = _default_mongo(host, port, usedb=db)

        for stock_type in self.stock_type_list:
            cursor = db[stock_collection].find({'stock_type': stock_type})

            for stock in cursor:
                stock_ids.append(stock['stock_id'])
        """
        stock_ids = []
        with open('stockIDs.txt') as f:
            for line in f:
                stock_ids.append(str(line).strip())

        log.msg('[stocks total count]: {stock_count}'.format(stock_count=len(stock_ids)))

        return stock_ids
