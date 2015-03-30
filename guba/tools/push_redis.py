# -*- coding: utf-8 -*-

from config import redis, mongo, GUBA_STOCK_COLLECTION

redis_key = "guba_stock_list_redis_spider:start_urls"

stock_type_list = ['沪A', '沪B', '深A', '深B']

for stock_type in stock_type_list:
    results = mongo[GUBA_STOCK_COLLECTION].find({"stock_type": stock_type})
    for r in results:
        stock_id = r['stock_id']
        url = "http://guba.eastmoney.com/list,%s,f.html" % stock_id
        redis.lpush(redis_key, url)

