# -*- coding: utf-8 -*-

import sys
import time
import json
from config import redis

url_list = []
with open ('../writedown.jl') as file:
    for line in file:
        line = json.loads(line)
        url_list.append(line['url'])

redis_key = 'dateback_detail_redis_spider:start_urls'

page = 0
for item_url in url_list:
    redis.lpush(redis_key, item_url)
    page+=1
    print "insert %d pages" %page


