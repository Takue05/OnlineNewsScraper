import scrapy

class NewsArticleItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    # content = scrapy.Field()
    newspaper = scrapy.Field()
    category = scrapy.Field()
    date = scrapy.Field()
    timestamp = scrapy.Field()  # For tracking when we scraped it