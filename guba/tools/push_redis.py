# -*- coding: utf-8 -*-

import sys
import time
from config import redis, mongo, GUBA_STOCK_COLLECTION

sel_stocks_count = int(sys.argv[1])

stock_ids = []
stock_count_dict = dict()
"""
with open('stock_count.txt') as f:
    for line in f:
        stock_id, count = line.strip().split(',')
        stock_count_dict[stock_id] = float(count)
"""

with open("stock_ids_2742.txt") as f:
    for line in f:
        stock_id = line.strip()
        stock_count_dict[stock_id] = 1

idx = 0
result = sorted(stock_count_dict.iteritems(), key=lambda (k, v): v, reverse=True)

for stock_id, count in result:
    stock_ids.append(stock_id)
    if idx >= sel_stocks_count - 1:
        break
    idx += 1

"""
with open('stock_ids_more_than_100.txt') as f:
    for line in f:
        count += 1
        stock_ids.append(line.strip())

with open('stock_ids_50_100.txt') as f:
    for line in f:
        stock_ids.append(line.strip())
        if count >= 59:
            break
        count += 1
"""

redis_key = "guba_stock_list_redis_spider:start_urls"
url = "http://guba.eastmoney.com/list,{stock_id},f.html"

while 1:
    for stock_id in stock_ids:
        redis.lpush(redis_key, url.format(stock_id=stock_id))

    print 'push redis: ', time.time(), ' sleep 1 minute...stock ids length: ', len(stock_ids)
    time.sleep(60)
