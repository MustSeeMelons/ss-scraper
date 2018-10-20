import scrapy
import json


class SpiderV1(scrapy.Spider):
    name = "Spider"
    start_urls = ["https://www.ss.com/lv/transport/cars/bmw/"]

    def parse(self, response):
        CAR_XPATH = ".//tr[contains(@id, \"tr_\")]"
        URL_XPATH = ".//a[contains(@id, \"dm_\")]"
        for car in response.xpath(CAR_XPATH):
            link = car.xpath(URL_XPATH).xpath("@href").extract_first()

            if link != None:
                yield scrapy.Request("https://www.ss.com" + str(link), callback=self.parseCar)

        # TODO fetch all pages
        # next_page = response.css('li.next a::attr("href")').extract_first()
        # if next_page is not None:
        #    yield response.follow(next_page, self.parse)

    def parseCar(self, response):
        DESC_XPATH = ".//div[contains(@id, \"msg_div_msg\")]/text()"

        arr = response.xpath(DESC_XPATH).extract()
        replaced = list(map(lambda s: str(s).replace("\r\n", " "), arr))
        joined = "".join(replaced)

        file = open("out.json", "a", encoding="utf-8")
        file.write(joined + "\n")
        file.close()

        # DESC_XPATH = ".//a[contains(@id, \"dm_\")]/text() | .//a[contains(@id, \"dm_\")]/b/text()"
        # yield {
        #     'desc': car.xpath(DESC_XPATH).extract(),
        # }
