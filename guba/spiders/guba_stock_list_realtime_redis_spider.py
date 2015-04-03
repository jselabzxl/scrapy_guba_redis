# -*- coding:utf-8 -*-

"""使用scrapy_redis的guba_stock_list_redis_spider(实时更新)
"""

import re
import json
import time
import math
import urllib2
from scrapy import log
from scrapy.http import Request
from scrapy.conf import settings
from scrapy.spider import Spider
from BeautifulSoup import BeautifulSoup
from guba.items import GubaPostListItem
from guba.middlewares import UnknownResponseError
from guba.utils import _default_redis, _default_mongo, HMS2ts, now_datestr
from guba.scrapy_redis.spiders import RedisSpider

HOST_URL = "http://guba.eastmoney.com/"
LIST_URL = HOST_URL + "list,{stock_id},f_{page}.html" # f表示按照发布时间排序

LATEST_POST_ID = 'latest_postid:{stock_id}'
host = settings.get('REDIS_HOST', None)
port = settings.get('REDIS_PORT', None)
redis = _default_redis(host, port)


class GubaStockListRtRedisSpider(RedisSpider):
    """usage: scrapy crawl guba_stock_list_realtime_redis_spider --loglevel=INFO
    """
    name = 'guba_stock_list_realtime_redis_spider'
    redis_key = 'guba_stock_list_redis_spider:start_urls'

    def parse(self, response):
        print 'response accepted: ', time.time()

        results = []
        resp = response.body
        try:
            page = response.meta['page']
        except KeyError:
            page = 1
        soup = BeautifulSoup(resp)

        try:
            headcode_span = soup.find("span", {"id": "stockheadercode"})
            stock_id = headcode_span.find("a").string
        except:
            raise UnknownResponseError

        # 已爬取的单支股票最新post_id
        latest_post_id = redis.get(LATEST_POST_ID.format(stock_id=stock_id))
        if latest_post_id:
            latest_post_id = int(latest_post_id)

        # 本次爬取任务最新的post_id
        newest_post_id = None

        stock_title = soup.html.head.title
        stock_name = re.search(r'_(.*?)股吧', str(stock_title)).group(1).decode('utf8')

        for item_soup in soup.findAll('div', {'class':'articleh'}):
            l1_span = item_soup.find("span", {"class": "l1"})
            clicks = int(l1_span.string)

            l2_span = item_soup.find("span", {"class": "l2"})
            replies = int(l2_span.string)

            isStockholder = False # 是否为股东
            isTopic = False # 话题
            isTop = False # 置顶
            isNews = False # 新闻
            em_info = None
            l3_span = item_soup.find("span", {"class": "l3"})
            em = l3_span.find("em")
            if em:
                em_info = em.text

            if em_info:
                if em_info == u'股友':
                    isStockholder = True
                elif em_info == u'话题':
                    isTopic = True
                elif em_info == u'置顶':
                    isTop = True
                elif em_info == u'新闻':
                    isNews = True

            # d表示按照时间排序回复
            post_url = HOST_URL + l3_span.find("a").get("href").replace('.html', ',d.html')
            post_id = int(re.search(r'news,.*?,(.*?),', post_url).group(1))
            post_title = l3_span.find("a").get("title")

            l4_span = item_soup.find("span", {"class": "l4"})
            l4_span_a = l4_span.find("a")

            if l4_span_a:
                user_name = l4_span_a.string
                try:
                    user_id = l4_span_a.get("data-popper")
                except:
                    user_id = l4_span_a.get("data-popstock")
                user_url = l4_span_a.get("href")
            else:
                user_name = l4_span.text
                user_id = None
                user_url = None

            l6_span = item_soup.find("span", {"class": "l6"})
            create_date = l6_span.text

            # 话题贴不属于该股吧，不存数据 
            if not isTopic:
                """
                # 对非置顶贴以及非新闻贴进行去重
                if not isTop and not isNews:
                    if latest_post_id and post_id <= latest_post_id:
                        break

                    if not newest_post_id or (newest_post_id and newest_post_id < post_id):
                        newest_post_id = post_id
                """

                item_dict = {'post_id': post_id, 'url': post_url, 'stock_id': stock_id, \
                'stock_name': stock_name, 'user_name': user_name, 'user_url': user_url, 'user_id': user_id, \
                'clicks': clicks, 'replies': replies, 'stockholder': isStockholder, 'create_date': create_date, \
                'em_info': em_info, 'title': post_title}

                item = GubaPostListItem()
                for key in GubaPostListItem.RESP_ITER_KEYS:
                    item[key] = item_dict[key]

                results.append(item)

        sorted_results = sorted(results, key=lambda item: item['post_id'], reverse=True)
        if len(sorted_results):
            newest_post_id = sorted_results[0]['post_id']

        results = filter(lambda item: item['post_id'] > latest_post_id, sorted_results)
        for r in results:
            print r['post_id'], latest_post_id

        if newest_post_id and newest_post_id > latest_post_id:
            redis.set(LATEST_POST_ID.format(stock_id=stock_id), newest_post_id)

        print 'parse complited: ', time.time()

        return results
