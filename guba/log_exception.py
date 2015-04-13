# -*- coding=utf-8 -*-

import re
import os
from twisted.internet import task
from scrapy.exceptions import NotConfigured
from scrapy import log, signals
from guba.utils import get_pid, get_ip
from scrapy.mail import MailSender


class LogStats(object):
    """Log basic scraping stats periodically"""

    def __init__(self, stats, interval, mailfrom, mailto, smtphost, smtpuser, smtppass, error_threshold):
        self.stats = stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.mailfrom = mailfrom
        self.mailto = mailto
        self.smtphost = smtphost
        self.smtpuser = smtpuser
        self.smtppass = smtppass
        self.error_threshold = error_threshold
        self.pid = get_pid()
        self.ip = get_ip()

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('LOGSTATS_INTERVAL')
        mailfrom = crawler.settings.get('WARNING_MAIL_FROM')
        mailto = crawler.settings.get('WARNING_MAIL_TO')
        smtphost = crawler.settings.get('WARNING_SMTP_HOST')
        smtpuser = crawler.settings.get('WARNING_SMTP_USER')
        smtppass = crawler.settings.get('WARNING_SMTP_PASS')
        error_threshold = crawler.settings.get('ERROR_THRESHOLD')
        if not interval:
            raise NotConfigured
        o = cls(crawler.stats, interval, mailfrom, mailto, smtphost, smtpuser, smtppass, error_threshold)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0
        self.exception_countprev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        exception_count = self.stats.get_value('downloader/exception_count',0)

        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        errrate = (exception_count - self.exception_countprev) * self.multiplier

        self.pagesprev, self.itemsprev, self.exception_countprev= pages, items, exception_count
        msg = "Crawled %d pages (at %d pages/min), scraped %d items (at %d items/min), raised %d exceptions (at %d exceptions/min), current ip is %s, current pid is %s" \
            % (pages, prate, items, irate, exception_count, errrate, self.ip, self.pid)
        log.msg(msg, spider=spider)

        if errrate > self.error_threshold:
            mailer = MailSender(smtphost=self.smtphost, mailfrom=self.mailfrom, smtpuser=self.smtpuser, smtppass=self.smtppass)
            mailer.send(to=[self.mailto], subject="Scrapy guba redis Error Warning", body="Exception rate has reached to %d,\n current ip is %s, current pid is %s" \
                    % (errrate, self.ip, self.pid))

    def spider_closed(self, spider, reason):
        if self.task.running:
            self.task.stop()

