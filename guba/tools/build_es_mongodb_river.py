#-*-coding=utf-8-*-

import os

"""
del_command_base = "curl -XDELETE 'http://%s:%s/_river/river_guba_post_%s'"
with open("stock_ids_2742.txt") as f:
    for line in f:
        stock_id = line.strip()
        command = del_command_base % ("219.224.135.94", "9200", stock_id)
        output = os.popen(command)
        print output.read()

"""
command_base = "curl -XPUT 'http://%s:%s/_river/river_guba_post_%s/_meta' -d '{ \"type\": \"mongodb\", \"mongodb\": { \"servers\": [ { \"host\": %s, \"port\": %s } ], \"db\": %s, \"collection\": %s}, \"index\": {\"name\": %s, \"type\": %s}}'"

with open("stock_ids_2742.txt") as f:
    for line in f:
        stock_id = line.strip()
        if stock_id == '600001':
            continue
        command = command_base % ("219.224.135.94", "9200", stock_id, "\"219.224.135.94\"", "\"27020\"", "\"guba\"", "\"post_stock_" + stock_id + "\"", "\"" + stock_id + "\"", "\"219_224_135_94_27020\"")
        output = os.popen(command)
        print output.read()
