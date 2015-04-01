# -*- coding: utf-8 -*-
"""统计所有股票的帖子总数(redis)
"""

import sys
import time
from config import redis, mongo, GUBA_POST_COLLECTION_PREFIX

mode = sys.argv[1] # list or detail

results = mongo.collection_names()
stock_ids = [r.lstrip(GUBA_POST_COLLECTION_PREFIX) for r in results if r.startswith(GUBA_POST_COLLECTION_PREFIX)]

total_count = 0
while 1:
    start_count = total_count
    total_count = 0
    for stock_id in stock_ids:
        total_count += redis.llen('%s:%s_items' % (stock_id, mode))

    print total_count - start_count
    time.sleep(60)
