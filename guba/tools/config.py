# -*- coding: utf-8 -*-

import redis
import pymongo

REDIS_HOST = '172.17.13.203'
REDIS_PORT = 6379
MONGOD_HOST = '172.17.13.207'
MONGOD_PORT = 27020
MONGOD_DB = 'guba'
GUBA_POST_COLLECTION_PREFIX = 'post_stock_'
GUBA_STOCK_COLLECTION = 'stock'
MONGODUMP = '/home/ubuntu3/linhao/mongodump/'

def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGOD_DB):
    # 强制写journal，并强制safe
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    # db = connection.admin
    # db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

mongo = _default_mongo()

def _default_redis(host=REDIS_HOST, port=REDIS_PORT, db=0):
    return redis.StrictRedis(host, port, db)

redis = _default_redis()

