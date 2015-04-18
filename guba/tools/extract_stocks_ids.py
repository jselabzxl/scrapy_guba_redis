# -*- coding: utf-8 -*-

from config import redis, _default_mongo, GUBA_STOCK_COLLECTION

mongo = _default_mongo(host="219.224.135.47", port=27019)

stock_type_list = ['沪A', '沪B', '深A', '深B']
stock_ids = []

for stock_type in stock_type_list:
    results = mongo[GUBA_STOCK_COLLECTION].find({"stock_type": stock_type})
    for r in results:
        stock_id = r['stock_id']
        stock_ids.append(stock_id)

print len(stock_ids)

f = open("stock_ids_2742.txt", "w")
for stock_id in stock_ids:
    f.write("%s\n" % stock_id)
f.close()
