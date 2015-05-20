#-*-coding=utf-8-*-

import os

command_base = "curl -XPUT 'http://%s:%s/_river/river_guba_post_%s/_meta' -d '{ \"type\": \"mongodb\", \"mongodb\": { \"servers\": [ { \"host\": %s, \"port\": %s } ], \"db\": %s, \"collection\": %s}, \"index\": {\"name\": %s, \"type\": %s}}'"

with open("stock_ids_2742.txt") as f:
    for line in f:
        stock_id = line.strip()
        command = command_base % ("172.17.13.207", "9200", stock_id + "_95", "\"172.17.13.208\"", "\"27020\"", "\"guba\"", "\"post_stock_" + stock_id + "\"", "\"post_stock_" + stock_id + "\"", "\"172.17.13.208_27020\"")
        output = os.popen(command)
        print output.read()
        command = command_base % ("172.17.13.207", "9200", stock_id + "_94", "\"172.17.13.207\"", "\"27020\"", "\"guba\"", "\"post_stock_" + stock_id + "\"", "\"post_stock_" + stock_id + "\"", "\"172.17.13.207_27020\"")
        output = os.popen(command)
        print output.read()
