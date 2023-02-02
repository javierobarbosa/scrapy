# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NeweggSpiderItem(scrapy.Item):
    link: scrapy.Field()
    name: scrapy.Field()
    manufacturer: scrapy.Field()
    model: scrapy.Field()
    price: scrapy.Field()
    price_currency: scrapy.Field()
    category: scrapy.Field()
    category_tree: scrapy.Field()
    availability: scrapy.Field()
    warranty: scrapy.Field()