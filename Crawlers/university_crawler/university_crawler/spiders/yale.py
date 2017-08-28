from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from university_crawler.items import BasicCrawlerItem
from scrapy.http import Request
from bs4 import BeautifulSoup
import re

#write all results from an individual page to a row of a text file
class MySpider(BaseSpider):
    name = "university_crawler" #Project name
    allowed_domains = ['www.yale.edu/'] #The bounds of the project
    start_urls = ["ttps://www.yale.edu/"] #The starting page for the project
    
    #Each dictionary item should represent a single page:
    #   with items['text'] as a concatenated string text elements
    #   and items['link'] as the url of the page
    items = {} 

    #Recursively crawls links gathered within, starting with start_url
    def parse(self, response): 
        hxs = Selector(response) #response from url
        pageText = "" #string to concatenate with text elements
               
        #Extract text, from the body, from h1-h6 headings, and from paragraphs
        results = hxs.xpath('body//h1/text() | body//h2/text() | body//h3/text() | body//h4/text() | body//h5/text() | body//h6/text() | body//p/text()').extract()
        
        #for every text result extracted
        for item in results:
            result = BasicCrawlerItem() 
            rawText = BeautifulSoup(item).getText() #use beautifulSoup to get rid of encodings
            rawText = rawText.strip('\n') #strip newline
            rawText = rawText.strip('\t') #strip tabs
            result["text"] = rawText #Put the text into the BasicCrawlerItem item "text"
            pageText += (rawText + " ") #Append the text to the pageText
            result["location_url"] = response.url #Put the url into the BasicCrawlerItem item "location_url"
            yield result
            
        self.items['text'] = pageText #Add the concatenated string containing page text into the items dictionary
        self.items['link'] = response.url #Add the url into the items dictionary
        
        #Write to a text file
        with open('yale.txt', 'a') as textWriter:
            textWriter.write(self.items['text'])
            #textWriter.write("link: " + self.items['link'] + 'name: ' + self.items['text'])
             
        #List of links already visited: used to avoid re-visiting pages
        visited_links=[]
        #Extract all links from current url
        links = hxs.xpath('//a/@href').extract()
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
