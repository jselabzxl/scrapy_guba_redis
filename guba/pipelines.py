# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import json
import socket
import pymongo
from scrapy import log
from twisted.internet.threads import deferToThread
from guba.items import GubaPostListItem, GubaStocksItem, GubaPostDetailItem, GubaPostDetailAllItem
from guba.utils import _default_mongo, mkdir_p, gen_key
from guba.naivebayes_classifier.naivebayes_classifier import naivebayes as nb_classifier


class JsonWriterPipeline(object):
    def __init__(self):
        mkdir_p('data')
        mkdir_p('data_list')
        mkdir_p('data_detail')

    def process_item(self, item, spider):
        if isinstance(item, GubaPostDetailAllItem):
            self.file = open('./data/items_%s.jl' % item['stock_id'], 'a')
            line = json.dumps(item.to_dict()) + "\n"
            self.file.write(line)

            return item

        if isinstance(item, GubaPostListItem):
            self.file = open('./data_list/items_list_%s.jl' % item['stock_id'], 'a')
            line = json.dumps(item.to_dict()) + "\n"
            self.file.write(line)

            return item

        if isinstance(item, GubaPostDetailItem):
            self.file = open('./data_detail/items_detail_%s.jl' % item['stock_id'], 'a')
            line = json.dumps(item.to_dict()) + "\n"
            self.file.write(line)

            return item


class MongodbPipeline(object):
    def __init__(self, db, host, port, post_collection_prefix, stock_collection, mongodb_host_port_list, hash_mongo):
        self.host = host
        self.port = port
        self.db = _default_mongo(host, port, usedb=db)
        self.stock_collection = stock_collection
        self.post_collection_prefix = post_collection_prefix
        self.hash_mongo = hash_mongo
        self.mongos_list = []
        for mongo in mongodb_host_port_list:
            mongo_host = mongo.split(":")[0]
            mongo_port = int(mongo.split(":")[1])
            mongos = _default_mongo(mongo_host, port=mongo_port, usedb=db)
            self.mongos_list.append(mongos)

        log.msg('Mongod connect to {host}:{port}:{db}'.format(host=host, port=port, db=db), level=log.INFO)

    @classmethod
    def from_settings(cls, settings):
        db = settings.get('MONGOD_DB', None)
        host = settings.get('MONGOD_HOST', None)
        port = settings.get('MONGOD_PORT', None)
        stock_collection = settings.get('GUBA_STOCK_COLLECTION', None)
        post_collection_prefix = settings.get('GUBA_POST_COLLECTION_PREFIX', None)
        mongodb_host_port_list = settings.get('MONGOD_HOST_PORT_LIST', None)
        hash_mongo = settings.get('HASH_MONGO', None)

        return cls(db, host, port, post_collection_prefix, stock_collection, mongodb_host_port_list, hash_mongo)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, GubaStocksItem):
            return deferToThread(self.process_stock, item, spider)
        elif isinstance(item, GubaPostListItem):
            return deferToThread(self.process_post_list, item, spider)
        elif isinstance(item, GubaPostDetailItem):
            return deferToThread(self.process_post_detail, item, spider)

    def process_item_sync(self, item, spider):
        if isinstance(item, GubaStocksItem):
            return self.process_stock(item, spider)
        elif isinstance(item, GubaPostListItem):
            return self.process_post_list(item, spider)
        elif isinstance(item, GubaPostDetailItem):
            return self.process_post_detail(item, spider)

    def mongos_hash(self, idstr):
        """根据idstr进行hash取mongos入口
        """
        key = gen_key(idstr)
        mongos = self.mongos_list[key % len(self.mongos_list)]
        return mongos

    def update_post_detail(self, post_collection, post):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaPostDetailItem.PIPED_UPDATE_KEYS:
            if post.get(key) is not None:
                updates[key] = post[key]

        updates_modifier = {'$set': updates}
        if self.hash_mongo:
            db = self.mongos_hash(str(post['_id']))
        else:
            db = self.db
        db[post_collection].update({'_id': post['_id']}, updates_modifier)

    def process_post_detail(self, item, spider):
        post = item.to_dict()
        post['_id'] = post['post_id']
        post['sentiment'] = nb_classifier(post)
        stock_id = post['stock_id']
        post_collection = self.post_collection_prefix + stock_id

        if self.hash_mongo:
            db = self.mongos_hash(str(post['_id']))
        else:
            db = self.db

        if db[post_collection].find({'_id': post['_id']}).count():
            self.update_post_detail(post_collection, post)
        else:
            try:
                post['first_in'] = time.time()
                post['last_modify'] = post['first_in']
                db[post_collection].insert(post)
            except pymongo.errors.DuplicateKeyError:
                self.update_post_detail(post_collection, post)

        return item

    def update_post_list(self, post_collection, post):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaPostListItem.PIPED_UPDATE_KEYS:
            if post.get(key) is not None:
                updates[key] = post[key]

        updates_modifier = {'$set': updates}
        if self.hash_mongo:
            db = self.mongos_hash(str(post['_id']))
        else:
            db = self.db
        db[post_collection].update({'_id': post['_id']}, updates_modifier)

    def process_post_list(self, item, spider):
        post = item.to_dict()
        post['_id'] = post['post_id']
        stock_id = post['stock_id']
        post_collection = self.post_collection_prefix + stock_id

        if self.hash_mongo:
            db = self.mongos_hash(str(post['_id']))
        else:
            db = self.db
        if db[post_collection].find({'_id': post['_id']}).count():
            self.update_post_list(post_collection, post)
        else:
            try:
                post['first_in'] = time.time()
                post['last_modify'] = post['first_in']
                db[post_collection].insert(post)
            except pymongo.errors.DuplicateKeyError:
                self.update_post_list(post_collection, post)

        return item

    def update_stock(self, stock_collection, stock):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaStocksItem.PIPED_UPDATE_KEYS:
            if stock.get(key) is not None:
                updates[key] = stock[key]

        updates_modifier = {'$set': updates}
        self.db[stock_collection].update({'_id': stock['_id']}, updates_modifier)

    def process_stock(self, item, spider):
        stock = item.to_dict()
        stock['_id'] = stock['stock_id']

        if self.db[self.stock_collection].find({'_id': stock['_id']}).count():
            self.update_stock(self.stock_collection, stock)
        else:
            try:
                stock['first_in'] = time.time()
                stock['last_modify'] = stock['first_in']
                self.db[self.stock_collection].insert(stock)
            except pymongo.errors.DuplicateKeyError:
                self.update_stock(self.stock_collection, stock)

        return item

import connection
from scrapy.utils.serialize import ScrapyJSONEncoder

class RedisStoragePipeline(object):
    def __init__(self, server):
        self.server = server
        self.encoder = ScrapyJSONEncoder()

    @classmethod
    def from_settings(cls, settings):
        server = connection.from_settings(settings)
        return cls(server)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        data = self.encoder.encode(item)
        if isinstance(item, GubaPostListItem):
            key = self.item_key_list(item, spider)
        if isinstance(item, GubaPostDetailItem):
            key = self.item_key_detail(item, spider)
        self.server.rpush(key, data)

        return item

    def item_key_list(self, item, spider):
        stock_id = item['stock_id']
        return "%s:list_items" % stock_id

    def item_key_detail(self, item, spider):
        stock_id = item['stock_id']
        return "%s:detail_items" % stock_id
