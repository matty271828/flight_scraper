import scrapy


class RoutesSpider(scrapy.Spider):
    name = "routes"
    start_urls = [
        'https://www.flightsfrom.com/MAN',
        'https://www.flightsfrom.com/LPL',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }