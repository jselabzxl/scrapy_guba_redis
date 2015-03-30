# -*- coding: utf-8 -*-

import pymongo


MONGOD_HOST = '219.224.135.60'
MONGOD_PORT = 27019
MONGOD_DB = 'guba'
GUBA_POST_COLLECTION_PREFIX = 'post_stock_'
MONGODUMP = '/home/ubuntu3/linhao/mongodump/'

def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGOD_DB):
    # 强制写journal，并强制safe
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    # db = connection.admin
    # db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

mongo = _default_mongo()
