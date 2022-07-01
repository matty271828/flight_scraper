# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightScraperItem(scrapy.Item):
    # Define the fields for your item here like:
    day = scrapy.Field()
    month = scrapy.Field()
    year = scrapy.Field()
    origin_id = scrapy.Field()
    destination_id = scrapy.Field()
    price = scrapy.Field()          
    
