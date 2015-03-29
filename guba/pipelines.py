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
from guba.items import GubaPostListItem, GubaPostItem, GubaStocksItem, GubaPostDetailItem, GubaPostDetailAllItem
from guba.utils import _default_mongo, mkdir_p


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
    def __init__(self, db, host, port, post_collection, stock_collection, post_list_collection):
        self.db_name = db
        self.host = host
        self.port = port
        self.db = _default_mongo(host, port, usedb=db)
        self.post_collection = post_collection
        self.stock_collection = stock_collection
        self.post_list_collection = post_list_collection
        log.msg('Mongod connect to {host}:{port}:{db}'.format(host=host, port=port, db=db), level=log.INFO)

    @classmethod
    def from_settings(cls, settings):
        db = settings.get('MONGOD_DB', None)
        host = settings.get('MONGOD_HOST', None)
        port = settings.get('MONGOD_PORT', None)
        post_collection = settings.get('GUBA_POST_COLLECTION', None)
        stock_collection = settings.get('GUBA_STOCK_COLLECTION', None)
        post_list_collection = settings.get('GUBA_POST_LIST_COLLECTION', None)

        return cls(db, host, port, post_collection, stock_collection, post_list_collection)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        if isinstance(item, GubaPostItem):
            return deferToThread(self.process_post, item, spider)
        elif isinstance(item, GubaStocksItem):
            return deferToThread(self.process_stock, item, spider)
        elif isinstance(item, GubaPostListItem):
            return deferToThread(self.process_post_list, item, spider)
        elif isinstance(item, GubaPostDetailItem):
            return deferToThread(self.process_post_detail, item, spider)

    def process_item_sync(self, item, spider):
        if isinstance(item, GubaPostItem):
            return self.process_post(item, spider)
        elif isinstance(item, GubaStocksItem):
            return self.process_stock(item, spider)
        elif isinstance(item, GubaPostListItem):
            return self.process_post_list(item, spider)
        elif isinstance(item, GubaPostDetailItem):
            return self.process_post_detail(item, spider)

    def update_post_detail(self, post_collection, post):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaPostDetailItem.PIPED_UPDATE_KEYS:
            if post.get(key) is not None:
                updates[key] = post[key]

        updates_modifier = {'$set': updates}
        self.db[post_collection].update({'_id': post['_id']}, updates_modifier)

    def process_post_detail(self, item, spider):
        post = item.to_dict()
        post['_id'] = post['post_id']

        if self.db[self.post_list_collection].find({'_id': post['_id']}).count():
            self.update_post_detail(self.post_list_collection, post)
        else:
            try:
                post['first_in'] = time.time()
                post['last_modify'] = post['first_in']
                self.db[self.post_list_collection].insert(post)
            except pymongo.errors.DuplicateKeyError:
                self.update_post_detail(self.post_list_collection, post)

        return item

    def update_post_list(self, post_collection, post):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaPostListItem.PIPED_UPDATE_KEYS:
            if post.get(key) is not None:
                updates[key] = post[key]

        updates_modifier = {'$set': updates}
        self.db[post_collection].update({'_id': post['_id']}, updates_modifier)

    def process_post_list(self, item, spider):
        post = item.to_dict()
        post['_id'] = post['post_id']

        if self.db[self.post_list_collection].find({'_id': post['_id']}).count():
            self.update_post_list(self.post_list_collection, post)
        else:
            try:
                post['first_in'] = time.time()
                post['last_modify'] = post['first_in']
                self.db[self.post_list_collection].insert(post)
            except pymongo.errors.DuplicateKeyError:
                self.update_post_list(self.post_list_collection, post)

        return item

    def update_post(self, post_collection, post):
        updates = {}
        updates['last_modify'] = time.time()
        for key in GubaPostItem.PIPED_UPDATE_KEYS:
            if post.get(key) is not None:
                updates[key] = post[key]

        updates_modifier = {'$set': updates}
        self.db[post_collection].update({'_id': post['_id']}, updates_modifier)

    def process_post(self, item, spider):
        post = item.to_dict()
        post['_id'] = post['post_id']

        if self.db[self.post_collection].find({'_id': post['_id']}).count():
            self.update_post(self.post_collection, post)
        else:
            try:
                post['first_in'] = time.time()
                post['last_modify'] = post['first_in']
                self.db[self.post_collection].insert(post)
            except pymongo.errors.DuplicateKeyError:
                self.update_post(self.post_collection, post)

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

