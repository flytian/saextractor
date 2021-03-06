__author__ = 'LeoDong'

import logging
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

from util import tool, config
import logging
from SAECrawlers.items import UrlItem


class PagesCrawler(CrawlSpider):
    name = "retriever"
    allowed_domains = config.retriever_allow_domains
    start_urls = config.retriever_start_urls

    rules = [
        Rule(LxmlLinkExtractor(allow_domains=config.retriever_allow_domains,
                               deny_domains=config.retriever_deny_domains,
                               deny_extensions=config.retriever_deny_extensions,
                               unique=True,
                               deny=config.retriever_deny_regxs
                               ),
             callback='parse_item',
             follow=True)
    ]

    def parse_start_url(self, response):
        return self.parse_item(response)

    @staticmethod
    def parse_item(response):
        # response are all updated or new
        # db not changed
        # is this url in URL_LIB
        item = UrlItem.load_with_content(url=response.url, response=response)
        logging.info("PC get page [%s]:- %s" % (item['id'], item['url']))
        yield item
