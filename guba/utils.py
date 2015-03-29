# -*- coding: utf-8 -*-

import time
import pymongo
import os, errno
from datetime import datetime


MONGOD_HOST = 'localhost'
MONGOD_PORT = 27017


def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb='test'):
    # 强制写journal，并强制safe
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    # db = connection.admin
    # db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

def now_datestr():
    return time.strftime('%m-%d', time.localtime(time.time()))


def datetimestr2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d')))


def postdate2ts(date):
    return int(time.mktime(time.strptime(datetime.now().strftime("%Y-") + date, '%Y-%m-%d')))


def HMS2ts(date):
    return int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: 
            raise
