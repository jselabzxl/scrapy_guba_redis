# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class GubaPostDetailAllItem(Item):
    """股吧detail页面完整字段
    """
    stock_id = Field() # stock id
    post_id = Field() # 帖子唯一标识
    content = Field() # 内容
    releaseTime = Field() # 发表时间
    lastReplyTime = Field() # 最后回复时间

    RESP_ITER_KEYS = ['stock_id', 'post_id', 'content', 'releaseTime', 'lastReplyTime']

    PIPED_UPDATE_KEYS = RESP_ITER_KEYS

    def __init__(self):
        super(GubaPostDetailAllItem, self).__init__()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (GubaPostDetailAllItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d

class GubaPostDetailItem(Item):
    """股吧detail页面字段
    """
    post_id = Field() # 帖子唯一标识
    content = Field() # 内容
    releaseTime = Field() # 发表时间
    lastReplyTime = Field() # 最后回复时间
    stock_id = Field() # 股票代码

    RESP_ITER_KEYS = ['post_id', 'content', 'releaseTime', 'lastReplyTime', 'stock_id']

    PIPED_UPDATE_KEYS = RESP_ITER_KEYS

    def __init__(self):
        super(GubaPostDetailItem, self).__init__()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (GubaPostDetailItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d

class GubaPostListItem(Item):
    """股吧列表页面字段
    """
    post_id = Field() # 帖子唯一标识
    title = Field() # 帖子标题
    url = Field() # 帖子url
    stock_name = Field() # 股票名称
    stock_id = Field() # 股票代码
    user_name = Field() # 作者昵称
    user_url = Field() # 作者url
    user_id = Field() # 作者id
    clicks = Field() # 点击数
    replies = Field() # 回复数
    stockholder = Field() # 是否是股东, True or False
    em_info = Field() #
    create_date = Field() # '12-01'

    RESP_ITER_KEYS = ['post_id', 'url', 'stock_id', \
            'stock_name', 'user_name', 'user_url', 'user_id', \
            'clicks', 'replies', 'stockholder', 'em_info', 'title', 'create_date']

    PIPED_UPDATE_KEYS = RESP_ITER_KEYS

    def __init__(self):
        super(GubaPostListItem, self).__init__()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (GubaPostListItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d

class GubaStocksItem(Item):
    stock_id = Field()
    stock_name = Field()
    stock_type = Field()
    stock_url = Field()

    RESP_ITER_KEYS = ['stock_id', 'stock_name', 'stock_type', 'stock_url']
    
    PIPED_UPDATE_KEYS = ['stock_name', 'stock_type', 'stock_url']

    def __init__(self):
        super(GubaStocksItem, self).__init__()

    def to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, (GubaPostItem, GubaStocksItem)):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d
