import scrapy
from selenium import webdriver
import time

class RouteSpider(scrapy.Spider):
    name = "route_spider"

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse_routes)

    def parse_routes(self, response):
        # To open a new browser window and navigate it
        driver = webdriver.Chrome()  
        
        # Use headless option to not open a new browser window
        #options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        #desired_capabilities = options.to_capabilities()
        #driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

        driver.get('https://www.flightsfrom.com/MAN')

        time.sleep(10)