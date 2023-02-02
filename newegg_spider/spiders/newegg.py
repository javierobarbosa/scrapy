import json
from scrapy import Spider
from scrapy.http import Request


class NeweggSpider(Spider):
    name = 'newegg'
    allowed_domains = ['newegg.com']
    start_urls = ['https://www.newegg.com/Electronics/Store/ID-10']

    def parse(self, response):
        categories = ['TV & Video', 'Home Video Accessories', 'Coffee Makers', 'Cooks Tools']
        for category in categories:
            url= "//a[text()='" + category + "']/@href"
            category_url  = response.xpath(url).extract_first()
            if category_url:
                yield Request(category_url, 
                            callback=self.parse_category)

    def parse_category(self, response):
        shop_category = response.xpath('//dl[contains(dt, "Shop Category")]/dd')
        subcategory_url = shop_category.xpath('.//a/@href').extract()
        titles = shop_category.xpath('.//a/text()').extract()
        for url in subcategory_url:
            yield Request(url,
                        callback=self.parse_subcategory)
    
    def parse_subcategory(self, response):
        product_urls= response.xpath('//a[contains(@class, "item-img")]/@href').extract()
        for url in product_urls:
            yield Request(url,
                        callback=self.parse_product)

        next_page = response.xpath('//link[@rel="next"]/@href').extract_first()
        if next_page:
            yield Request(next_page,
                          callback=self.parse_subcategory)

    def parse_product(self, response):
        def get_currency():
            windows_state_data = response.xpath('//script[contains(text(),"currency")]/text()').extract_first()
            if windows_state_data:
                window_state_obj = json.loads(windows_state_data.split("=")[1])
                currency = window_state_obj.get('currency')['currencyCode']
            return currency   

        def get_warranty():
            warranty = ""
            warranty_query = '//*[contains(@class, "product-additional-info")]//div[@class="info-item" and .//h4[contains(., "Warranty")]]'
            warranty_data = response.xpath(warranty_query)
            if warranty_data:
                for li in warranty_data.xpath('.//li'):
                    warranty_item = li.xpath('text()').extract()
                    if warranty_item:
                        warranty += ''.join(warranty_item) +'\n'
            return warranty

        def get_price():
            int_part = response.xpath('//div[@class="product-price"]/ul/li[@class="price-current"]/strong/text()').extract_first() or ""
            decimal_part = response.xpath('//div[@class="product-price"]/ul/li[@class="price-current"]/sup/text()').extract_first() or ""
            return int_part + decimal_part

        def get_manufacturer():
            manufacturer = response.xpath('//th[text()="Brand"]/following-sibling::td/text()').extract_first()            
            return manufacturer
        
        def get_model():
            model = response.xpath('//th[text()="Model"]/following-sibling::td/text()').extract_first()            
            return model

        output = {}
        output['Item Link'] = response.url        

        product_data =  response.xpath('//div[@class="product-wrap"]')
        output['Item Name'] = product_data.xpath('.//h1[@class="product-title"]/text()').extract_first()

        manufacturer = ""
        model = ""
        price = ""
        price_currency = ""

        xpath_query = '//*[@class="page-section-inner"]/script[@type="application/ld+json"]/text()'
        json_description = response.xpath(xpath_query).extract_first()
        product_description = {}
        if json_description:
            product_description = json.loads(json_description)

            manufacturer = product_description.get('brand')
            model = product_description.get('Model')
            offer_data = product_description.get('offers')
            if offer_data:
                price = offer_data.get('price')
                price_currency = offer_data.get('priceCurrency')

        output['Manufacturer'] = manufacturer or get_manufacturer()
        output['Model'] = model or get_model()
        output['Item Price'] = price or get_price()
        output['Price Currency'] = price_currency or get_currency()

        category_list = response.xpath('//ol[@class="breadcrumb"]/li/a/text()').extract()
        output['Item Category Tree'] = "/".join(category_list)

        output['Item Category'] = category_list[1] if category_list else ""

        availability = product_data.xpath('.//div[@class="product-inventory"]/strong/text()').extract_first() or ""        
        output['Availability'] = availability.replace(".", "").strip()

        output['OEM Warranty'] = get_warranty()

        yield output
