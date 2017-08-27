from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from university_crawler.items import BasicCrawlerItem
from scrapy.http import Request
from bs4 import BeautifulSoup
import re

#write all results from an individual page to a row of a text file
class MySpider(BaseSpider):
    name = "university_crawler"
    allowed_domains = ['www.yale.edu']
    start_urls = ["https://www.yale.edu/"]
    
    items = {}

    def parse(self, response):
        hxs = Selector(response)   
        pageText = ""
               
        results = hxs.xpath('body//h1/text() | body//h2/text() | body//h3/text() | body//h4/text() | body//h5/text() | body//h6/text() | body//p/text()').extract()
        
        for item in results:
            result = BasicCrawlerItem()
            rawText = BeautifulSoup(item).getText()
            result["text"] = rawText
            pageText += (rawText + " ")
            result["location_url"] = response.url
            yield result
            
        self.items['text'] = pageText
        self.items['link'] = response.url
        
        with open('yale.txt', 'a') as textWriter:
            textWriter.write("link: " + self.items['link'] + 'name: ' + self.items['text'])
                      
        visited_links=[]
        links = hxs.xpath('//a/@href').extract()
        link_validator= re.compile("^(?:http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

        for link in links:
            if link_validator.match(link) and not link in visited_links:
                visited_links.append(link)
                yield Request(link, self.parse)
            else:
                full_url=response.urljoin(link)
                visited_links.append(full_url)
                yield Request(full_url, self.parse)
