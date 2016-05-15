# -*- coding: utf-8 -*-

# Scrapy settings for guba project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

import os

BOT_NAME = 'guba'

SPIDER_MODULES = ['guba.spiders']
NEWSPIDER_MODULE = 'guba.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'guba (+http://www.yourdomain.com)'

# The amount of time (in secs) that the downloader should wait 
# before downloading consecutive pages from the same spider
DOWNLOAD_DELAY = 0.05 # 50 ms of delay

# If enabled, Scrapy will wait a random amount of time 
# (between 0.5 and 1.5 * DOWNLOAD_DELAY) while fetching requests 
# from the same spider.
# This randomization decreases the chance of the crawler 
# being detected (and subsequently blocked) by sites which analyze 
# requests looking for statistically significant similarities in 
# the time between their requests.
# RANDOMIZE_DOWNLOAD_DELAY = True

# 期望减少mongodb的压力
# Maximum number of concurrent items (per response) to process in parallel in ItemPipeline, Default 100
CONCURRENT_ITEMS = 1000
# The maximum number of concurrent (ie. simultaneous) requests that will be performed by the Scrapy downloader, Default 16.
CONCURRENT_REQUESTS = 160
# The maximum number of concurrent (ie. simultaneous) requests that will be performed to any single domain, Default: 8.
CONCURRENT_REQUESTS_PER_DOMAIN = 80

CONCURRENT_REQUESTS_PER_IP = 100

# 不需要默认的180秒,更多的机会留给重试
# The amount of time (in secs) that the downloader will wait before timing out, Default: 180.
DOWNLOAD_TIMEOUT = 180

#AUTOTHROTTLE_ENABLED = True # Enables the AutoThrottle extension.
#AUTOTHROTTLE_START_DELAY = 2.0 # The initial download delay (in seconds).Default: 5.0
#AUTOTHROTTLE_MAX_DELAY = 60.0 # The maximum download delay (in seconds) to be set in case of high latencies.
#AUTOTHROTTLE_CONCURRENCY_CHECK_PERIOD = 100 # How many responses should pass to perform concurrency adjustments.
#AUTOTHROTTLE_DEBUG = True


SPIDER_MIDDLEWARES = {
    # Filters out Requests for URLs outside the domains covered by the spider.
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,

    # Populates Request Referer header, based on the URL of the Response which generated it.
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': None,

    # Filters out requests with URLs longer than URLLENGTH_LIMIT
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': None,

    # DepthMiddleware is a scrape middleware used for tracking the depth of 
    # each Request inside the site being scraped. It can be used to limit 
    # the maximum depth to scrape or things like that.
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': None,

    # Filter out unsuccessful (erroneous) HTTP responses so that spiders 
    # don’t have to deal with them, which (most of the time) imposes an overhead, 
    # consumes more resources, and makes the spider logic more complex.
    # According to the HTTP standard, successful responses are those whose status codes are in the 200-300 range.
    # If you still want to process response codes outside that range, you can specify which response codes the spider 
    # is able to handle using the handle_httpstatus_list spider attribute or HTTPERROR_ALLOWED_CODES setting.
    'scrapy.contrib.spidermiddleware.httperror.HttpErrorMiddleware': None, # 50,

    # handle 403 forbidden error
    'guba.middlewares.Forbbiden403Middleware': 48,

    # handle 302 deleted error
    'guba.middlewares.Redirect302Middleware': 49,

    # retry forever middleware
    'guba.middlewares.RetryForeverMiddleware': 930,

    # retry 3 times middleware
    'guba.middlewares.RetryErrorResponseMiddleware': 940
}

DOWNLOADER_MIDDLEWARES = {
    # this middleware filters out requests forbidden by the robots.txt exclusion standard.
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': None,

    # This middleware authenticates all requests generated from certain spiders using Basic 
    # access authentication (aka. HTTP auth).
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': None,

    # proxy start
    'guba.middlewares.ProxyMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    # proxy end

    # This middleware sets the download timeout for requests specified in the DOWNLOAD_TIMEOUT setting.
    'scrapy.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware': 350,

    # handle downloadtimeout error
    'guba.middlewares.DownloadTimeoutRetryMiddleware': 375,

    # Middleware that allows spiders to override the default user agent.
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,

    # A middlware to retry failed requests that are potentially caused by temporary problems such as 
    # a connection timeout or HTTP 500 error.
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None, # 500,

    # This middleware sets all default requests headers specified in the :setting:`DEFAULT_REQUEST_HEADERS` setting.
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': None,

    # This middleware handles redirection of requests based on meta-refresh html tag.
    'scrapy.contrib.downloadermiddleware.redirect.MetaRefreshMiddleware': None, # 580,

    # This middleware allows compressed (gzip, deflate) traffic to be sent/received from web sites.
    'scrapy.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware': 590,

    # this middleware handles redirection of requests based on response status.
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,

    # This middleware enables working with sites that require cookies, such as 
    # those that use sessions. It keeps track of cookies sent by web servers, 
    # and send them back on subsequent requests (from that spider), just like web browsers do.
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': None,

    # This middleware adds support for chunked transfer encoding
    'scrapy.contrib.downloadermiddleware.chunked.ChunkedTransferMiddleware': 830,

    # Middleware that stores stats of all requests, responses and exceptions that pass through it.
    'scrapy.contrib.downloadermiddleware.stats.DownloaderStats': 850,

    # This middleware provides low-level cache to all HTTP requests and responses. 
    # It has to be combined with a cache storage backend as well as a cache policy.
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': None
}

ITEM_PIPELINES = {
    'guba.pipelines.MongodbPipeline': 300,
    # 'guba.pipelines.RedisStoragePipeline': 300,
    'guba.scrapy_redis.pipelines.RedisPipeline': 400,
    # 'guba.pipelines.JsonWriterPipeline': 800,
    # 'guba.pipelines.GubaPipeline': 200
}

EXTENSIONS = {
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None,
    'scrapy.contrib.logstats.LogStats': None,
    'guba.log_exception.LogStats':500
}

# HTTPERROR_ALLOWED_CODES = [403] # Pass all responses with non-200 status codes contained in this list for httperror middleware.

# If enabled, Scrapy will wait a random amount of time (between 0.5 and 1.5 * DOWNLOAD_DELAY)
# while fetching requests from the same website.
RANDOMIZE_DOWNLOAD_DELAY = True

REFERER_ENABLED = False # disable RefererMiddleware

# retry middleware settings
RETRY_TIMES = 3 # RetryMiddleware Maximum number of times to retry, in addition to the first download. RetryErrorResponseMiddleware 重试次数
RETRY_ENABLED = True
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408]
LOG_STDOUT = False

# RetryForeverMiddleware
RETRY_INIT_WAIT = 1 # 第一次重试等待1s
RETRY_STABLE_TIMES = 100 # 重试100次之后WAIT不再增加
RETRY_ADD_WAIT = 1 # 每次重试后增加的等待秒数

# MONGODB setting
HASH_MONGO = False # 表示通过hash选入口，False表示使用固定入口
MONGOD_HOST = '192.168.146.128'
MONGOD_PORT = 27017
#MONGOD_HOST_PORT_LIST = {'172.17.13.207:27020': 1, '172.17.13.208:27020': 0}
MONGOD_DB = 'guba'
GUBA_POST_COLLECTION_PREFIX = 'post_stock_'
GUBA_STOCK_COLLECTION = 'stock'

PROXY_FROM_REDIS = True
# Proxy ip list file
PROXY_IP_FILE = './guba/proxy_ips.txt'
PROXY_IP_REDIS_KEY = 'guba_proxy_ips:sorted_set'
PROXY_IP_PUNISH = 10000 # 每次IP访问失败增加的等待时间

# scrapy_redis中redis server的配置, # Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = '192.168.146.128'
REDIS_PORT = 7001
REDIS_STORAGE_HOST = '192.168.146.128'
REDIS_STORAGE_PORT = 7001

# Specify the full Redis URL for connecting (optional).
# If set, this takes precedence over the REDIS_HOST and REDIS_PORT settings.
# REDIS_URL = 'redis://user:pass@hostname:9001'

# 默认是使用scrapy.core.scheduler.Scheduler，现在使用scrapy_redis中实现的调度器。
SCHEDULER = "guba.scrapy_redis.scheduler.Scheduler"

# 不清空redis queue，允许爬取过程中暂停并恢复
SCHEDULER_PERSIST = True

# 默认使用的是SpiderPriorityQueue，也可以换成后两种
# SCHEDULER_QUEUE_CLASS = 'guba.scrapy_redis.queue.SpiderPriorityQueue'
# Schedule requests using a queue (FIFO).
SCHEDULER_QUEUE_CLASS = "guba.scrapy_redis.queue.SpiderQueue"
# Schedule requests using a stack (LIFO).
# SCHEDULER_QUEUE_CLASS = "guba.scrapy_redis.queue.SpiderStack"

# smtp server setting for warining
WARNING_MAIL_FROM = '15195817207@163.com'
WARNING_MAIL_TO = '15338706547@qq.com'
WARNING_SMTP_HOST = 'smtp.126.com'
WARNING_SMTP_USER = 'ykbuaa'
WARNING_SMTP_PASS = 'yuankuN'
ERROR_THRESHOLD = 5

