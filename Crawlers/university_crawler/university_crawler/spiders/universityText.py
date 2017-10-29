# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time

class ToScrapeSpiderXPath(CrawlSpider):
    name = 'universityText' #The name to call when running this spider (i.e. 'scrapy crawl universityText')
    allowed_domains = ['yale.edu'] #The domain bounds of the project
    start_urls = ["https://www.yale.edu/"] #The starting page(s) for the project
    
    #Extracts links from each page to allow chained crawling behaviour
    rules = (Rule(LinkExtractor(),callback='parse_item',follow=True),)

    #Runs once for each webpage:
    def parse_item(self, response):        
        pageText = "" #string to concatenate with text elements
        
        #Data to extract:
        responses = response.xpath("body//p")
        responses += response.xpath('body//h1')
        responses += response.xpath('body//h2')
        responses += response.xpath('body//h3')
        responses += response.xpath('body//h4')
        responses += response.xpath('body//h5')
        responses += response.xpath("body//h6")
        
        #For each element extracted
        for quote in responses:
            #Select the text, and strip of whitespace characters (incl '\n', '\t')
            for text in quote.xpath('normalize-space(.//text())').extract():
                #If there's anything left after whitespace characters have been removed:
                if text is not "":
                    #Add text element to the page's text
                    pageText += (text + ".")
                    
        # Yield an Item that has the page's URL under 'url', and the entire pageText string as 'text'      
        yield {
                'dateRetrieved': time.strftime("%c"),
                'url': response.url,
                'text': pageText               
                }                                 
            
