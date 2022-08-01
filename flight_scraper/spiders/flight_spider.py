import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime
import time
import random

from flight_scraper.items import FlightScraperItem
from run_sql import run_sql

# Run this spider by typing entering 'scrapy crawl flight_spider -o prices.json' into the command line

# Class 
class FlightSpider(scrapy.Spider):
    name = "flight_spider"

    # Using a dummy website to start scrapy request
    def start_requests(self):
        # Retrieve airport routes from database
        sql = "SELECT origin_id, destination_id FROM airport_routes"
        routes = run_sql(sql)

        url = "http://quotes.toscrape.com"

        # To search single route
        #yield scrapy.Request(url=url, callback=self.parse_prices, dont_filter=False, cb_kwargs={'source_city':'LHR', 'destination_city':'DXB'})
        
        # Iterate over multiple origins
        for i in range(0, 5):
            # Output to terminal
            print(f"Searching: {routes[i][0]} -> {routes[i][1]}")

            # Set dont_filter to 'True' to allow multiple requests to be sent
            yield scrapy.Request(url=url, callback=self.parse_prices, dont_filter=True, cb_kwargs={'source_city':routes[i][0], 'destination_city':routes[i][1]})
            # Wait before proceeding to next loop - IMPORTANT
            time.sleep(random.randint(2, 5))

    def parse_prices(self, response, source_city, destination_city):
        #--------------------------------- Parameters ------------------------------------------
        # Inputs
        url = "https://www.google.com/travel/flights"
        departure_date = str(date.today())

        # Required element xpaths
        source_city_XPATH = '//*[@id="i14"]/div[1]/div/div/div[1]/div/div/input'
        dropdown_selection_XPATH = '//*[@id="i14"]/div[6]/div[2]/div[2]/div[1]/div/input'
        destination_XPATH = '//*[@id="i14"]/div[4]/div/div/div[1]/div/div/input'
        trip_type_XPATH = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/div[1]/div[1]/div/button/span[1]'
        one_way_selection_XPATH = '//*[@id="ow19"]/div[2]/div[2]/ul/li[2]'
        departure_date_XPATH = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div/c-wiz/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/div[1]/div/input'
        calendar_grid_base_XPATH = '//*[@id="ow62"]/div[2]/div/div[2]/div[2]/div/div/div[1]/div/div'
        calendar_button_XPATH = '//*[@id="ow62"]/div[2]/div/div[2]/div[2]/div/div/div[3]/div/button'
        accept_cookies_XPATH = '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button'

        #--------------------------------- Begin driving browser ------------------------------------------
        # To open a new browser window and navigate it
        #driver = webdriver.Chrome()  

        # Create an instance of headless ChromeDriver
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

        # Open page
        driver.get(url)

        # Wait for page to load
        driver.implicitly_wait(10)

        # TODO - Add clicking on accepting cookies button
        accept_cookies = driver.find_element_by_xpath(accept_cookies_XPATH)
        accept_cookies.click()

        # Source city selection steps
        fly_from = driver.find_element_by_xpath(source_city_XPATH)
        fly_from.click()
        fly_from_text = driver.find_element_by_xpath(dropdown_selection_XPATH)
        fly_from_text.send_keys(source_city)
        fly_from_text.send_keys(Keys.ENTER)

        # Wait 1 second
        driver.implicitly_wait(5)
        
        # Destination city selection steps
        fly_to = driver.find_element_by_xpath(destination_XPATH)
        fly_to.click()
        fly_to_text = driver.find_element_by_xpath(dropdown_selection_XPATH)
        fly_to_text.send_keys(destination_city)
        fly_to_text.send_keys(Keys.ENTER)

        # Wait 2 second
        #driver.implicitly_wait(2)
        #time.sleep(2)

        # Select one way trip
        trip_type = driver.find_element_by_xpath(trip_type_XPATH)
        trip_type.click()
        driver.implicitly_wait(2)
        time.sleep(1)
        one_way = driver.find_element_by_xpath(one_way_selection_XPATH)
        one_way.click()

        time.sleep(2)

        # Depature date selection steps
        departure_date_element = driver.find_element_by_xpath(departure_date_XPATH)
        departure_date_element.click()
        driver.implicitly_wait(2)
        departure_date_element.send_keys(departure_date)
        departure_date_element.send_keys(Keys.ENTER)

        time.sleep(5)

        # Explicit wait
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, calendar_grid_base_XPATH)))

        #--------------------------------- Scraping ------------------------------------------

        # Open and close prices.json to clear it
        open('prices.json', 'w').close()

        # Iterate over each month in year
        for i in range(1, 13):

            # Calculate item_month and year represented
            item_month = datetime.now().month + (i - 1)
            item_year = datetime.now().year

            # December has been passed in loop
            if (item_month > 12):
                item_month = item_month - 12
                item_year = item_year + 1

            # Construct XPATH
            month_XPATH = calendar_grid_base_XPATH + '/div[' + str(i) + ']/div[3]'

            # Extract monthly data
            monthly_data = driver.find_elements_by_xpath(month_XPATH)
            # Use Scrapy's yield to store output to JSON file/Database
            for data in monthly_data:
                # Split string
                split_data = data.text.split("\n")

                # Construct list of flights
                # Each flight will be defined by a date and a price
                list_flights = []

                for j in range(0, len(split_data)):
                    # Check if substring is a date
                    if len(split_data[j]) < 3:
                        # Create and append new flight item
                        flight = []
                        item_day = split_data[j]
                        flight.append(item_day)

                        # Check for last substring edge case
                        if j == len(split_data) - 1:
                            pass

                        else:
                            # Check if subsequent substring also a date and complete item/list if so
                            if len(split_data[j+1]) < 3:
                                item_price = None
                                flight.append(None)
                                list_flights.append(flight)

                    # Else item is a price
                    else:
                        # Remove unicode character from string
                        item_price = split_data[j].replace('\u00a3','')
                        flight.append(item_price)   
                        list_flights.append(flight)        

                        # yield flightItem
                        flightItem = FlightScraperItem(day = item_day, month = item_month, year = item_year, origin_id = source_city, destination_id = destination_city, price = item_price)
                        yield flightItem

                # yield list - uncomment this and run command 'scrapy crawl flight_spider -o prices.json' to output to json file
                #yield {
                #   i-1:list_flights,
                #}

            # Click button to pan through calendar
            if i < 12 and i % 2 == 0:
                pan_calender = driver.find_element_by_xpath(calendar_button_XPATH)
                pan_calender.click()
                time.sleep(2)
                pan_calender.click()
                time.sleep(5)     

        #--------------------------------- Scraping ------------------------------------------
        time.sleep(30)
        # Quit driver
        driver.quit()
             