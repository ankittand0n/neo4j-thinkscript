import scrapy

class ThinkscriptItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    code_blocks = scrapy.Field()
    links = scrapy.Field()
    crawled_at = scrapy.Field() 