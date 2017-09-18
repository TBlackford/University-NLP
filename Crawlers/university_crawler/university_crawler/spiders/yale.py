# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re

class ToScrapeSpiderXPath(scrapy.Spider):
    name = 'yale'
    allowed_domains = ['www.yale.edu'] #The bounds of the project
    start_urls = ["https://www.yale.edu/"] #The starting page for the project

    #Runs once for each webpage:
    def parse(self, response):        
        pageText = "" #string to concatenate with text elements
        
        #Data to extract:
        responses = response.xpath("body//p")
        responses += response.xpath('body//h1')
        responses += response.xpath('body//h2')
        responses += response.xpath('body//h3')
        responses += response.xpath('body//h4')
        responses += response.xpath('body//h5')
        responses += response.xpath("body//h6")
        #responses += response.xpath("body//*[contains(@class, 'text')]")
        
        #For each element extracted
        for quote in responses:
            #Select the text, and strip of whitespace characters (incl '\n', '\t')
            for text in quote.xpath('normalize-space(.//text())').extract():
                #If there's anything left after the above process:
                if text is not "":
                    #Add text element to the page's text
                    pageText += (text + " ")
                    
        # Yield an Item that has the page's URL under 'url', and the entire pageText string as 'text'      
        yield {
                'url': response.url,
                'text': pageText
                }                    


        #List of links already visited: used to avoid re-visiting pages
        visited_links=[]
        #Extract all links from current url
        links = response.xpath('//a/@href').extract()
        link_validator= re.compile("^(?:http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

        #for all links extracted:
        for link in links:
            #If the link is valid, and hasn't already been visited:
            if link_validator.match(link) and not link in visited_links:
                #add to visited list
                visited_links.append(link)
                #Visit it
                yield Request(link, self.parse)
            else:
                full_url=response.urljoin(link)
                visited_links.append(full_url)
                yield Request(full_url, self.parse)                
            
