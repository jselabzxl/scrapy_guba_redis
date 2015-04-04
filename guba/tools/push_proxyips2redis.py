#-*- coding=utf-8 -*-

import time
from config import redis

redis_key = "guba_proxy_ips:sorted_set"

forbid_ips = set()
with open('ip_forbid.txt') as f:
    for line in f:
        forbid_ips.add(line.strip())

proxy_ips = set()
with open('../proxy_ips.txt') as f:
    for line in f:
        proxy_ip = line.strip()
        if proxy_ip not in forbid_ips:
            proxy_ips.add(proxy_ip)

print 'proxy ip list ', len(proxy_ips), ' push to redis'
redis.delete(redis_key)
for proxy_ip in proxy_ips:
    redis.zincrby(redis_key, proxy_ip, amount=1)
