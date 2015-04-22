#-*-coding=utf-8-*-

import os

command_base = "curl -XPUT 'http://%s:%s/_river/river_guba_post_%s/_meta' -d '{ \"type\": \"mongodb\", \"mongodb\": { \"servers\": [ { \"host\": %s, \"port\": %s } ], \"db\": %s, \"collection\": %s}, \"index\": {\"name\": %s, \"type\": %s}}'"

with open("stock_ids_2742.txt") as f:
    for line in f:
        stock_id = line.strip()
        if stock_id == '600001':
            continue
        command = command_base % ("219.224.135.94", "9200", stock_id + "_95", "\"219.224.135.95\"", "\"27020\"", "\"guba\"", "\"post_stock_" + stock_id + "\"", "\"post_stock_" + stock_id + "\"", "\"219_224_135_95_27020\"")
        output = os.popen(command)
        print output.read()
        command = command_base % ("219.224.135.94", "9200", stock_id + "_94", "\"219.224.135.94\"", "\"27020\"", "\"guba\"", "\"post_stock_" + stock_id + "\"", "\"post_stock_" + stock_id + "\"", "\"219_224_135_94_27020\"")
        output = os.popen(command)
        print output.read()
