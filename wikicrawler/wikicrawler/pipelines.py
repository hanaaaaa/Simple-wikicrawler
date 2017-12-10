# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
i = 0
class FilePipeline(object):
    def __init__(self):
        self.filename = open("entries.json","w")
    def process_item(self, item, spider):
        global i
        i = i + 1
        jsontext = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.filename.write(jsontext)
        return item
    def close_spider(self, spider):
        global i
        self.filename.write("\n共" + str(i) + "字条")
        self.filename.close()
