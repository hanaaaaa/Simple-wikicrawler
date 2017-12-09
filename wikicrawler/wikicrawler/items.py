# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class entryItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    name = Field()
    summary = Field()
    info = Field()
    content = Field()
    uptime = Field()
    refer =  Field()
    label = Field()