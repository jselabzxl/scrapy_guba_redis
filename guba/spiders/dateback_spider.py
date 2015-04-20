# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import re
import operator
import math
from guba.items import GubaPostListItem
from guba.middlewares import UnknownResponseError
from BeautifulSoup import BeautifulSoup
from scrapy import log
from scrapy.http import Request
from scrapy.spider import Spider
from guba.scrapy_redis.spiders import RedisSpider

HOST_URL = "http://guba.eastmoney.com/"
LIST_URL = HOST_URL + "list,{stock_id},f_{page}.html" # f表示按照发布时间排序


class GubaDateBackSpider(RedisSpider):

    """ usage: scrapy crawl dateback_spider_00 -a start_time="starttime" -a stop_time="stoptime" \
    -a stock_id=stock_id --loglevel=INFO """
    """ time_format=2015,3,31,9,59,0,0,90,0"""

    name = 'dateback_spider'
    def __init__(self,start_time,stop_time,stock_id):
        self.start_time=tuple(map(int,start_time.split(',')))
        self.stop_time=tuple(map(int,stop_time.split(',')))
        self.stock_id=stock_id

    def start_requests(self):

        stock_id=self.stock_id
        request=Request(LIST_URL.format(stock_id=self.stock_id,page=1))
        request.meta['stock_id']=stock_id
        request.meta['page']=1
        request.meta['year']=2015
        request.meta['last_create_date']=None

        yield request

    def parse(self,response):
        page = response.meta['page']
        date_year = response.meta['year']
        last_create_date = response.meta['last_create_date']
        print page

        stock_id=response.meta['stock_id']
        shift_start_time=time.mktime(self.start_time)
        shift_stop_time=time.mktime(self.stop_time)

        if shift_start_time > shift_stop_time:
            raise ValueError('stop_time and start_time are not correct')

        resp = response.body
        results = []
        try:
            page_ = response.xpath('//div[@class="pager"]/text()').extract()[0].strip()
            pagenum = int((re.search(ur'[\u4e00-\u9fa5]+ (\d*) [\u4e00-\u9fa5]+', page_)).group(1))
            page_number = math.ceil(pagenum/80)+1
            print page_number
        except:
            page_number = 1


        soup = BeautifulSoup(resp)
        try:
            headcode_span = soup.find("span", {"id": "stockheadercode"})
            stock_id = headcode_span.find("a").string
        except:
            raise UnknownResponseError

        stock_title = soup.html.head.title
        stock_name = re.search(r'_(.*?)股吧', str(stock_title)).group(1).decode('utf8')

        stoped = False
        if soup.find('div', {'class': 'noarticle'}):
            stoped = True

        for item_soup in soup.findAll('div', {'class':'articleh'}):    #解析网页数据
            l1_span = item_soup.find("span", {"class": "l1"})
            clicks = int(l1_span.string)

            l2_span = item_soup.find("span", {"class": "l2"})
            replies = int(l2_span.string)

            isStockholder = False
            isTopic = False
            em_info = None
            l3_span = item_soup.find("span", {"class": "l3"})
            em = l3_span.find("em")
            if em:
                em_info = em.text

            if em_info:
                if em_info == u'股东':
                    isStockholder = True
                elif em_info == u'话题' or em_info == u'公告' or em_info == u'新闻' or em_info == u'研报':
                    isTopic = True
                    continue

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

            if not isTopic:

                item_dict = {'post_id': post_id, 'url': post_url, 'stock_id': stock_id, \
                'stock_name': stock_name, 'user_name': user_name, 'user_url': user_url, 'user_id': user_id, \
                'clicks': clicks, 'replies': replies, 'stockholder': isStockholder, 'create_date': create_date, \
                'em_info': em_info, 'title': post_title}

                item = GubaPostListItem()
                for key in GubaPostListItem.RESP_ITER_KEYS:
                    item[key] = item_dict[key]
                results.append(item)


        results = sorted(results, key = operator.itemgetter('post_id'))    #按照post_id进行排序


        last_time_page = results[0]['create_date']


        if page == 1:
            date_year = self.page_year(results)
            last_create_date = [results[i]['create_date'] for i in range(5)]
        else:
            date_year = self.page_year(results,last_create_date,date_year)
            last_create_date = [results[i]['create_date'] for i in range(5)]
        print last_time_page,[results[i]['create_date'] for i in range(5)],date_year

        last_time=time.mktime(tuple([date_year,int(str(last_time_page).split('-')[0]),int(str(last_time_page).split('-')[1]),12,0,0,0,90,0]))


        if last_time > shift_stop_time:    #如果最后一个帖子的时间没有达到终止点，继续查找
            result =[]
            if page_number != 1:
                page+=1
                request=Request(LIST_URL.format(stock_id=self.stock_id,page=page))
                request.meta['stock_id'] = stock_id
                request.meta['page'] = page
                request.meta['year'] = date_year
                request.meta['last_create_date'] = last_create_date
                result.append(request)
                print page
            else:
                pass
            return result

        elif last_time >= shift_start_time and page_number != 1:

            result = []    #去重
            for item in results:
                create_date = item['create_date']
                if item == results[0]:
                    current_time = last_time
                else:
                    current_time = self.test_time(create_date,current_time)
                if ((current_time >= shift_start_time) and (current_time <= shift_stop_time)):
                    result.append(item) 
                    print current_time,shift_start_time
                else:
                    pass

            if page < page_number:    #判断是否到最后一页
                page+=1
                request=Request(LIST_URL.format(stock_id=self.stock_id,page=page))
                request.meta['stock_id'] = stock_id
                request.meta['page'] = page
                request.meta['year'] = date_year
                request.meta['last_create_date'] = last_create_date
                result.append(request)
            else:
                pass
            return result

        else:
            scrapy_continue = False
            create_date_set = set([item_results['create_date'] for item_results in results])    #判断多爬取的下一页中有没有剩余数据
            if time.strftime("%m-%d",self.start_time) in create_date_set or time.strftime("%m-%d",self.stop_time) in create_date_set:
                scrapy_continue = True
            print scrapy_continue

            result = []    #去重
            for item in results:
                create_date = item['create_date']
                if item == results[0]:
                    current_time = last_time
                else:
                    current_time = self.test_time(create_date,current_time)

                if (current_time >= shift_start_time) and (current_time <= shift_stop_time):
                    result.append(item) 
                    print current_time,shift_start_time
                else:
                    pass

            if page_number == 1 or page == page_number:    #如果只有一页，或者到达最后一页，停止向下爬取
                scrapy_continue = False

            if  scrapy_continue:   #多爬取一页，检验有无遗漏数据

                page+=1
                request=Request(LIST_URL.format(stock_id=self.stock_id,page=page))
                request.meta['stock_id'] = stock_id
                request.meta['page'] = page
                request.meta['year'] = date_year
                request.meta['last_create_date'] = last_create_date
                result.append(request)

            return result





    def page_year(self,content,last_create_date=None,local_year=time.localtime(time.time()).tm_year):    #判断一页中最有一条帖子的年份
        create_date_set = list([item_results['create_date'] for item_results in content])
        create_date_set.append(last_create_date)
        for i in range(len(create_date_set)-1):
            result1=cmp(str(create_date_set[i]).split('-')[0],str(create_date_set[i+1]).split('-')[0])
            if result1 == 1:
                result2 = cmp(str(create_date_set[i-1]).split('-')[0],str(create_date_set[i+1]).split('-')[0])
                if result2 != 0:
                    local_year=local_year-1
                else:
                    pass
            else:
                continue
        return local_year


    def test_time(self,content,next_time):
        next_time_format = time.gmtime(next_time)
        [current_month,current_day] = map(int,content.split('-'))
        if current_month >= next_time_format[1]:
            return time.mktime((next_time_format[0],current_month,current_day,next_time_format[3],next_time_format[4],next_time_format[5],next_time_format[6],next_time_format[7],next_time_format[8]))
        else:
            return time.mktime((next_time_format[0]+1,current_month,current_day,next_time_format[3],next_time_format[4],next_time_format[5],next_time_format[6],next_time_format[7],next_time_format[8]))

