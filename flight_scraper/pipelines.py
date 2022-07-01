# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2

# Data-fields
DATABASE_URL = 'postgres://matthewmaclean:123@localhost:5432/flights_db'

class FlightScraperPipeline:
    def open_spider(self, spider):
        hostname = 'localhost'
        username = 'matthewmaclean'
        password = '123'
        database = 'flights_db'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        try:
            self.cur.execute("INSERT INTO flights_prototype_data (day, month, year, origin_id, destination_id, price) VALUES (%s, %s, %s, %s, %s, %s)", (item['day'], item['month'], item['year'], item['origin_id'], item['destination_id'], item['price']))
        except psycopg2.errors.InFailedSqlTransaction:
            pass    

        self.connection.commit()
        return item
