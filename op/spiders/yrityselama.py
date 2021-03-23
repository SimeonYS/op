import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import OpItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'
base = 'https://www.op-media.fi/contentapi/theme-pages?themeId=12946&take=20&skip={}'


class YrityselamaSpider(scrapy.Spider):
    name = 'yrityselama'
    offset = 0
    start_urls = [base.format(offset)]
    ITEM_PIPELINES = {
        'yrityselama.pipelines.OpPipeline': 300,

    }

    def parse(self, response):
        data = json.loads(response.text)
        for index in range(len(data['contentPages'])):
            link = data['contentPages'][index]['url']
            yield response.follow(link, self.parse_post)
        if data['pagesLeft']:
            self.offset += 20
            yield response.follow(base.format(self.offset), self.parse)


    def parse_post(self, response):
        date = response.xpath(
            '(//span[@class="font-default leading-md text-color-default xl:text-color-large text-default xl:text-md"])[last()]/text() | //div[@class="person-block__published"]/span[last()]/text()').get()
        title = response.xpath('//h1/text()').get()
        content = response.xpath(
            '//div[@class="article__main | pb-xl sm:pb-xxl xl:pb-xxxl ds-col ds-col--lg-8 ds-col--xl-7"]//text() | //div[@class="main-content dropcap-container | flex flex-col mb-xs md:max-w-main-content md:mx-auto"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=OpItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

