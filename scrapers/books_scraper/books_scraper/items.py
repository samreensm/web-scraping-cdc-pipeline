# # Define here the models for your scraped items
# #
# # See documentation in:
# # https://docs.scrapy.org/en/latest/topics/items.html

# from dataclasses import dataclass


# @dataclass
# class BooksScraperItem:
#     # define the fields for your item here like:
#     # name: str | None = None
#     pass

import scrapy


class BookItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    availability = scrapy.Field()