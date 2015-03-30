# -*- coding: utf-8 -*-
"""统计所有股票的帖子总数
"""

from config import _default_mongo, GUBA_POST_COLLECTION_PREFIX

mongo = _default_mongo()

results = mongo.collection_names()
collection_names = [r for r in results if r.startswith(GUBA_POST_COLLECTION_PREFIX)]

total_count = 0
for col in collection_names:
    total_count += mongo[col].count()

print total_count
