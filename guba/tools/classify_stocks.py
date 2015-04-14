#-*-coding=utf-8-*-
"""根据股票的活yue度提取股票
"""

import pymongo
from config import mongo

func='''
        function(obj,prev)
        {
            prev.count++;
        }
'''

start_datestr = "2014-10-01 00:00:00"
end_datestr = "2014-11-01 00:00:00"

results = mongo["stock"].find()
stock_ids = [r["stock_id"] for r in results]

"""
fw = open('stock_count.txt', 'w')
fw1 = open('stock_ids_more_than_100.txt', 'w')
fw2 = open('stock_ids_50_100.txt', 'w')
stock_count_t = 0
max_count = 0
sel = 0
for stock_id in stock_ids:
    count = mongo["post"].find({"stock_id": stock_id, "releaseTime": {"$gte": start_datestr, '$lt': end_datestr}}).count()

    count = float(count) / 31.0
    if count > max_count:
        max_count = count
        sel = stock_id

    if count > 100:
        fw1.write('%s\n' % stock_id)
    stock_count_t += count

    if count > 50 and count <= 100:
        fw2.write('%s\n' % stock_id)

    if count > 0:
        fw.write('%s,%s\n' % (stock_id, count))

print stock_count_t, sel, max_count
fw1.close()
fw2.close()
fw.close()
"""
daily_total_count = 0
with open('stock_count.txt') as f:
    for line in f:
        stock_id, count = line.strip().split(',')
        daily_total_count += float(count)
print daily_total_count

fw3 = open('stock_ids_40_50.txt', 'w')
fw4 = open('stock_ids_30_40.txt', 'w')
fw5 = open('stock_ids_20_30.txt', 'w')
fw6 = open('stock_ids_10_20.txt', 'w')
fw7 = open('stock_ids_0_10.txt', 'w')
with open('stock_count.txt') as f:
    for line in f:
        stock_id, count = line.strip().split(',')
        count = float(count)
        if count <= 50 and count > 40:
            fw3.write('%s\n' % stock_id)

        if count <= 40 and count > 30:
            fw4.write('%s\n' % stock_id)

        if count <= 30 and count > 20:
            fw5.write('%s\n' % stock_id)

        if count <= 20 and count > 10:
            fw6.write('%s\n' % stock_id)

        if count <= 10 and count > 0:
            fw7.write('%s\n' % stock_id)
fw3.close()
fw4.close()
fw5.close()
fw6.close()
fw7.close()
