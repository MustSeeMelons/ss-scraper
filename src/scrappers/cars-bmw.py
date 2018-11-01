from datetime import datetime
import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import csv

class SpiderV1(scrapy.Spider):
    name = 'bmw'
    startUrl = 'https://www.ss.com/lv/transport/cars/bmw/'
    pageCounter = 1

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print('This should have information on how long it took.')

    def start_requests(self):
        dt = datetime.now()
        self.fileName = '../../output/'+self.name + \
            '_' + str(dt.microsecond) + '.csv'

        with open(self.fileName, 'a', newline='', encoding='utf8') as f:
            writer = csv.writer(f)
            writer.writerow(['make', 'desc', 'year', 'engine',
                             'gearbox', 'mileage', 'ta', 'price', 'link'])

        return [scrapy.FormRequest(self.startUrl)]

    def parse(self, response):
        CAR_XPATH = './/tr[contains(@id, \"tr_\")]'
        URL_XPATH = './/a[contains(@id, \"dm_\")]'

        for car in response.xpath(CAR_XPATH):
            link = car.xpath(URL_XPATH).xpath('@href').extract_first()

            if link != None:
                yield scrapy.Request('https://www.ss.com' + str(link), callback=self.parseCar)

        self.pageCounter += 1
        yield scrapy.Request(self.startUrl + 'page' + str(self.pageCounter) + '.html', callback=self.parse)

    def parseCar(self, response):
        DESC_XPATH = './/div[contains(@id, \"msg_div_msg\")]/text()'
        MAKE_XPATH = './/td[contains(@id, \"tdo_31\")]/b/text()'
        YEAR_XPATH = './/td[contains(@id, \"tdo_18\")]/text()'
        ENGINE_XPATH = './/td[contains(@id, \"tdo_15\")]/text()'
        GEARBOX_XPATH = './/td[contains(@id, \"tdo_35\")]/text()'
        MILEAGE_XPATH = './/td[contains(@id, \"tdo_16\")]/text()'
        TA_XPATH = './/td[contains(@id, \"tdo_223\")]/text()'
        PRICE_XPATH = './/td[contains(@id, \"tdo_8\")]/text()|.//span[contains(@id, \"tdo_8\")]/text()'

        # Description
        arr = response.xpath(DESC_XPATH).extract()  # Array of lines of text

        eol = map(lambda s: str(s).replace('\r\n', ' '), arr)  # EOL
        lf = map(lambda s: str(s).replace('\n', ' '), eol)  # LF
        cr = list(map(lambda s: str(s).replace('\r', ' '), lf))  # CR

        desc = ''.join(cr)

        # Make
        make = response.xpath(MAKE_XPATH).extract_first()
        # Year
        year = response.xpath(YEAR_XPATH).extract_first()
        # Engine
        engine = response.xpath(ENGINE_XPATH).extract_first()
        # Gearbox
        gearbox = response.xpath(GEARBOX_XPATH).extract_first()
        # Mileage
        mileage = response.xpath(MILEAGE_XPATH).extract_first()
        # TA
        ta = ''
        taExtract = response.xpath(TA_XPATH).extract_first()
        try:
            ta = '{:06.4f}'.format(taExtract)
        except:
            ta = str(taExtract)

        # Price
        price = response.xpath(PRICE_XPATH).extract_first()

        file = open(self.fileName, 'a', newline='', encoding='utf8')
        writer = csv.writer(file)
        writer.writerow([make, desc, year, engine, gearbox,
                         mileage, ta, price, response.request.url])
        file.close()

