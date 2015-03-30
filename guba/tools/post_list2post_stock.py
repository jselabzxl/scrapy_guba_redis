# -*- coding: utf-8 -*-

import time
from datetime import datetime
from config import mongo, MONGODUMP, GUBA_POST_COLLECTION_PREFIX
from bs_input import KeyValueBSONInput

XAPIAN_FLUSH_DB_SIZE = 1000

GUBA_POST_LIST_COLLECTION = 'post_list'
bson_file = MONGODUMP + 'guba/' + GUBA_POST_LIST_COLLECTION + '.bson'

post_list_keys = [u'stock_id', u'user_id', u'releaseTime', u'user_url', u'url', \
        u'lastReplyTime', u'stockholder', u'stock_name', u'content', \
        u'post_id', u'em_info', u'last_modify', u'replies', u'title', \
        u'create_date', u'_id', u'user_name', u'clicks', u'first_in']

bs_input = KeyValueBSONInput(open(bson_file, 'rb'))

count = 0
ts = time.time()
for _id, item in bs_input.reads():
    try:
        item_new = dict()
        for key in post_list_keys:
            item_new[key] = item[key]

        stock_id = item_new['stock_id']
        mongo[GUBA_POST_COLLECTION_PREFIX + stock_id].save(item_new)

    except KeyError:
        pass

    count += 1
    if count % XAPIAN_FLUSH_DB_SIZE == 0:
        te = time.time()
        cost = te - ts
        ts = te
        print '[%s] total write: %s, %s sec/per %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), count, cost, XAPIAN_FLUSH_DB_SIZE)

bs_input.close()
