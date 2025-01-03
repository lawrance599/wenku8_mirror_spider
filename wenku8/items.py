# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    query_id: int = scrapy.Field()
    title: str = scrapy.Field()
    writer: str = scrapy.Field()
    description: str = scrapy.Field()
    last_chapter: str = scrapy.Field()
    last_updated: str = scrapy.Field()
    words: int = scrapy.Field()
    status: str = scrapy.Field()
    tags: list[str] = scrapy.Field()


class TextItem(scrapy.Item):
    id: int = scrapy.Field()
    content: bytes = scrapy.Field()


class CoverItem(scrapy.Item):
    id: int = scrapy.Field()
    content: bytes = scrapy.Field()
