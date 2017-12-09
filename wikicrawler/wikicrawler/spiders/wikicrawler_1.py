"""
本爬虫从wiki英文的A-Z索引页面开始入手，在所有索引中不断爬取词条信息
主要爬取出词条访问URL地址、词条名称、词条简介、词条基本信息、词条目录及内容、词条更新时间、参考资料、词条标签
8个部分的信息，最后存储在entryItem中。
"""



import scrapy
from scrapy import Request, Selector
from ..items import entryItem

import re


class wikicrawler_1(scrapy.Spider):
    name = "wikicrawler_1"
    start_urls = ["https://en.wikipedia.org/wiki/Portal:Contents/A%E2%80%93Z_index"]
    host = "https://en.wikipedia.org"

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=self.start_urls, callback=self.parse)



    # 处理主页的函数
    def parse(self, response):
        selector = Selector(response)
        content = selector.xpath("//table[@id='toc']//tr//td//a")
        for index in content:
            i = index.xpath("string(.)").extract_first()
            index_url = index.xpath("@href").extract_first()
            url = self.host + index_url
            yield Request(url=url, callback=self.parse_mainindex)



    # 处理索引页面的函数
    def parse_mainindex(self, response):
        selector = Selector(response)
        content = selector.xpath("//div[@class='mw-allpages-body']/ul//li//a")

        for index in content:
            name = index.xpath("string(.)").extract_first()
            index_url = index.xpath("@href").extract_first()
            url = self.host + index_url
            yield Request(url=url, callback=self.parse_index)

        # 处理翻页
        page = selector.xpath("//div[@class='mw-allpages-nav']/a[2]")
        nextpage = page.xpath("@href").extract_first()
        if nextpage:
            nextpage_url = self.host + nextpage
            yield Request(url=nextpage_url, callback=self.parse_mainindex)



    # 爬取词条内容的函数
    def parse_index(self, response):
        selector = Selector(response)


        # 词条url
        print(response.url)


        # 词条名称name
        name_node = selector.xpath("//h1")
        name = name_node.xpath("string(.)").extract_first()


        # 词条信息
        info_node = selector.xpath("//div[@id='toc']/preceding-sibling::p")
        info = ""
        for infor in info_node:
            info += "\n" + infor.xpath("string(.)").extract_first()


        # 词条目录及内容content，以字典存储
        content_node = selector.xpath("//div[@id='toc']//li")
        content_list = []
        for title in content_node:
            content_name = title.xpath("string(.)").extract_first()
            truename = re.search(r'(?<=\d).\w{2,}.*', content_name, flags=0).group()
            content_list.append(truename)
        content = dict.fromkeys(tuple(content_list))
        keys = list(content.keys())
        for i, key in enumerate(keys):
            link = re.sub(r'\s', '_', key[1:], count=0, flags=0)

            # 对上一次循环中多余的内容进行删减
            if i > 0:
                topic_clears = selector.xpath("//span[@id='" + link + "']/../preceding-sibling::p| \
                                            //span[@id='" + link + "']/../preceding-sibling::ul| \
                                            //span[@id='" + link + "']/../preceding-sibling::div")
                topic_clearlist = []
                for topic_clear in topic_clears:
                    topic_clearlist.append(topic_clear.xpath('string(.)').extract_first())
                source_list = content[keys[i - 1]]
                content[keys[i - 1]] = [a for a in topic_clearlist if a in source_list]

            topics = selector.xpath("//span[@id='" + link + "']/../following-sibling::p| \
                                    //span[@id='" + link + "']/../following-sibling::ul| \
                                    //span[@id='" + link + "']/../following-sibling::div")
            topic_contend = []
            for topic in topics:
                topic_contend.append(topic.xpath('string(.)').extract_first())
            content[key] = topic_contend


        # 简介
        if ' Overview' in content:
            summary = content[' Overview']
        else:
            summary = []
        print(summary)


        # 更新时间uptime
        uptime_node = selector.xpath("//li[@id='footer-info-lastmod']")
        uptime_sentence = uptime_node.xpath("string(.)").extract_first()
        uptime = re.search(r'\d+.*(?=\.)', uptime_sentence, flags=0).group()
        uptime = re.sub(r'\s\bat\b\s', '', uptime, count=0, flags=0)


        # 参考资料refer，以列表存储
        refer_node = selector.xpath("//span[@id='References']/../following-sibling::div//ol[@class='references']/li")
        refer = []
        for references in refer_node:
            refer.append(references.xpath("string(.)").extract_first())


        # 词条标签label，即其分类，以列表存储
        label_node = selector.xpath("//div[@id='mw-normal-catlinks']/ul/li")
        label = []
        for labels in label_node:
            label.append(labels.xpath("string(.)").extract_first())


        item = entryItem()
        item["url"] = response.url
        item["name"] = name
        item["summary"] = summary
        item["info"] = info
        item["content"] = content
        item["uptime"] = uptime
        item["refer"] = refer
        item["label"] = label
        yield item




