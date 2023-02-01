import scrapy
import re

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    start_urls = []
    for i in range(1,20):
        start_urls.append(f'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{i}')

    def parse(self, response):
        for product in response.xpath('//div[@class="a-section a-spacing-small a-spacing-top-small"]'):
            review_data = product.xpath('.//span[@class="a-size-base s-underline-text"]/text()').get()
            pattern = re.compile(r'\w+\,?\w*').findall(f'{review_data}')

            yield {
                'Product_url': f'''https://www.amazon.in/{product.xpath('.//h2[@class="a-size-mini a-spacing-none a-color-base s-line-clamp-2"]/a/@href').get()}''',
                'Product_Name': product.xpath('.//span[@class="a-size-medium a-color-base a-text-normal"]/text()').get(),
                'Product_Price': product.xpath('.//span[@class="a-offscreen"]/text()').get(),
                'Rating': product.xpath('.//span[@class="a-icon-alt"]/text()').get(),
                'Number_of_reviews': pattern[0]
            }


