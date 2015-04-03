# -*- coding: utf-8 -*-

import time
from config import redis, mongo, GUBA_STOCK_COLLECTION

stock_ids = []
f = open('stock_ids_more_than_100.txt')
count = 0
for line in f:
    if count >= 15:
        break
    count += 1
    stock_ids.append(line.strip())
f.close()
print 'stock ids: ', len(stock_ids)

redis_key = "guba_stock_list_redis_spider:start_urls"
url = "http://guba.eastmoney.com/list,{stock_id},f.html"

while 1:
    for stock_id in stock_ids:
        redis.lpush(redis_key, url.format(stock_id=stock_id))

    print 'push redis: ', time.time(), ' sleep 1 minute...'
    time.sleep(60)

"""
stock_type_list = ['沪A', '沪B', '深A', '深B']

for stock_type in stock_type_list:
    results = mongo[GUBA_STOCK_COLLECTION].find({"stock_type": stock_type})
    for r in results:
        stock_id = r['stock_id']
        url = "http://guba.eastmoney.com/list,%s,f.html" % stock_id
        redis.lpush(redis_key, url)
"""
