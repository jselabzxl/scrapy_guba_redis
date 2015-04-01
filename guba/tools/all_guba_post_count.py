# -*- coding: utf-8 -*-
"""统计所有股票的帖子总数(mongodb)
"""

import sys
import time
from config import _default_mongo, GUBA_POST_COLLECTION_PREFIX

mode = sys.argv[1] # list or detail

mongo = _default_mongo()

results = mongo.collection_names()
collection_names = [r for r in results if r.startswith(GUBA_POST_COLLECTION_PREFIX)]

total_count = 0
while 1:
    start_count = total_count
    total_count = 0
    for col in collection_names:
        if mode == 'detail':
            total_count += mongo[col].find({"content": {"$exists": True}}).count()
        elif mode == 'list'::
            total_count += mongo[col].find().count()

    print total_count - start_count
    time.sleep(60)
