import sys
sys.path.append("..")

from datetime import datetime
import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import csv
from abc import ABC, abstractmethod

from utils.utils import startTimer, endTimer, Sanitizer

class SingleCar(scrapy.Spider):
    name = 'car'
    startUrl = 'https://www.ss.com/lv/transport/cars/'
    pageCounter = 1

    @abstractmethod
    def get_name(self):
        pass

    def __init__(self, callback = None):
        startTimer()
        self.name = self.get_name()
        self.startUrl = self.startUrl + self.name + '/'
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.callback = callback

    def spider_closed(self, spider):
        endTimer()
        if self.callback != None:
            print(self.fileName)
            self.callback()

    def start_requests(self):
        dt = datetime.now()
        self.fileName = './output/'+self.name + \
            '_' + str(dt.microsecond) + '.csv'

        with open(self.fileName, 'a', newline='', encoding='utf8') as f:
            writer = csv.writer(f)
            writer.writerow(['make', 'desc', 'year', 'engine', 'engine type'
                             'gearbox', 'mileage', 'body', 'ta', 'price', 'location', 'link'])

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
        MAKE_XPATH = './/td[contains(@id, \"tdo_31\")]/b/text()|.//td[contains(@id, \"tdo_24\")]/b/text()'
        YEAR_XPATH = './/td[contains(@id, \"tdo_18\")]/text()'
        ENGINE_XPATH = './/td[contains(@id, \"tdo_15\")]/text()'
        GEARBOX_XPATH = './/td[contains(@id, \"tdo_35\")]/text()'
        MILEAGE_XPATH = './/td[contains(@id, \"tdo_16\")]/text()'
        TA_XPATH = './/td[contains(@id, \"tdo_223\")]/text()'
        PRICE_XPATH = './/td[contains(@id, \"tdo_8\")]/text()|.//span[contains(@id, \"tdo_8\")]/text()'
        BODY_XPATH = './/td[contains(@id, \"tdo_32\")]/text()'
        LOCATION_XPATH = './/td[@class=\"ads_contacts\"]/text()'

        # Description
        arr = response.xpath(DESC_XPATH).extract()  # Array of lines of text

        eol = map(lambda s: str(s).replace('\r\n', ' '), arr)  # EOL
        lf = map(lambda s: str(s).replace('\n', ' '), eol)  # LF
        cr = list(map(lambda s: str(s).replace('\r', ' '), lf))  # CR

        desc = ''.join(cr)

        # Make
        make = response.xpath(MAKE_XPATH).extract_first()
        # Year
        year = Sanitizer.sanitizeDate(
            response.xpath(YEAR_XPATH).extract_first())

        # Engine & engine type
        engine = None
        engineType = None
        engine_str = response.xpath(ENGINE_XPATH).extract_first()
        if engine_str != None:
            split = engine_str.split()
            engine = split[0]
            if len(split) > 1:
                engineType = split[1]

        # Gearbox
        gearbox = response.xpath(GEARBOX_XPATH).extract_first()
        # Mileage
        mileage = Sanitizer.sanitizeMileage(
            response.xpath(MILEAGE_XPATH).extract_first())
        # TA
        ta = Sanitizer.sanitizeInspection(
            response.xpath(TA_XPATH).extract_first())
        # Price
        price = Sanitizer.sanitizePrice(
            response.xpath(PRICE_XPATH).extract_first())
        # Body
        body = response.xpath(BODY_XPATH).extract_first()
        # Location
        contacts = response.xpath(LOCATION_XPATH).extract()
        location = next(
            contact for contact in contacts if contact != None and contact != ' ')

        if Sanitizer.isCarValid(make, price, ta):
            file = open(self.fileName, 'a', newline='', encoding='utf8')
            writer = csv.writer(file)
            writer.writerow([make, desc, year, engine, engineType, gearbox,
                             mileage, body, ta, price, location, response.request.url])
            file.close()


class AllCars(SingleCar):
    pageCounters = {}
    ignored = list([
        '/lv/transport/cars/exchange/',
        '/lv/transport/other/transport-with-defects-or-after-crash/',
        '/lv/transport/service-centers-and-checkup/',
        '/lv/transport/service-centers-and-checkup/transportation-and-evacuation/',
        '/lv/transport/transports-rent/',
        '/lv/transport/other/trailers/',
        '/lv/transport/spare-parts/',
        '/lv/transport/spare-parts/trunks-wheels/',
        '/lv/transport/other/transport-for-invalids/',
        '/lv/transport/service-centers-and-checkup/tuning/'
    ])

    def __init__(self, callback = None):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.callback = callback

    def parse(self, response):
        BRAND_XPATH = './/h4[contains(@id, \"sc_\")]/a'

        for category in response.xpath(BRAND_XPATH):
            link = category.xpath('@href').extract_first()

            if link not in self.ignored:
                categoryLink = 'https://www.ss.com' + str(link)
                self.pageCounters[categoryLink] = 1
                yield scrapy.Request(categoryLink, callback=self.parseCategory)

    def parseCategory(self, response):
        CAR_XPATH = './/tr[contains(@id, \"tr_\")]'
        URL_XPATH = './/a[contains(@id, \"dm_\")]'

        for car in response.xpath(CAR_XPATH):
            link = car.xpath(URL_XPATH).xpath('@href').extract_first()

            if link != None:
                yield scrapy.Request('https://www.ss.com' + str(link), callback=self.parseCar)

        self.pageCounters[self.getRootLink(response.request.url)] += 1
        rootLink = self.getRootLink(response.request.url)
        yield scrapy.Request(rootLink + 'page' + str(self.pageCounters[rootLink]) + '.html', callback=self.parseCategory)

    def getRootLink(self, url):
        try:
            index = url.index('page')
            return url[:index]
        except:
            return url


def scrape(scraper):
    process = CrawlerProcess(get_project_settings())
    process.crawl(scraper)
    process.start()

def threadedScraper(scraper):
    process = CrawlerProcess(get_project_settings())
    process.crawl(scraper)
    
    def start():
        process.start()
    
    return start

# A lot of small classes follow, one for each car brand


def scrapeAll():
    car = AllCars()
    scrape(car)


class Audi(SingleCar):
    def get_name(self):
        return 'audi'


def scrapeAudi():
    car = Audi()
    scrape(car)


class BMW(SingleCar):
    def get_name(self):
        return 'bmw'


def scrapeBmw():
    car = BMW()
    scrape(car)


class AlfaRomeo(SingleCar):
    def get_name(self):
        return 'alfa-romeo'


def scrapeAlfaRomeo():
    car = AlfaRomeo()
    scrape(car)


class Cadillac(SingleCar):
    def get_name(self):
        return 'cadillac'


def scrapeCadillac():
    car = Cadillac()
    scrape(car)


class Chevrolet(SingleCar):
    def get_name(self):
        return 'chevrolet'


def scrapeChevrolet():
    car = Chevrolet()
    scrape(car)


class Chrysler(SingleCar):
    def get_name(self):
        return 'chrysler'


def scrapeChrysler():
    car = Chrysler()
    scrape(car)


class Citroen(SingleCar):
    def get_name(self):
        return 'citroen'


def scrapeCitroen():
    car = Citroen()
    scrape(car)


class Dacia(SingleCar):
    def get_name(self):
        return 'dacia'


def scrapeDacia():
    car = Dacia()
    scrape(car)


class Dodge(SingleCar):
    def get_name(self):
        return 'dodge'


def scrapeDodge():
    car = Dodge()
    scrape(car)


class Fiat(SingleCar):
    def get_name(self):
        return 'fiat'


def scrapeFiat():
    car = Fiat()
    scrape(car)


class Ford(SingleCar):
    def get_name(self):
        return 'ford'


def scrapeFord():
    car = Ford()
    scrape(car)


class Honda(SingleCar):
    def get_name(self):
        return 'honda'


def scrapeHonda():
    car = Honda()
    scrape(car)


class Hyundai(SingleCar):
    def get_name(self):
        return 'hyundai'


def scrapeHyundai():
    car = Hyundai()
    scrape(car)


class Infiniti(SingleCar):
    def get_name(self):
        return 'infiniti'


def scrapeInfiniti():
    car = Infiniti()
    scrape(car)


class Jaguar(SingleCar):
    def get_name(self):
        return 'dacia'


def scrapeJaguar():
    car = Jaguar()
    scrape(car)


class Jeep(SingleCar):
    def get_name(self):
        return 'jeep'


def scrapeJeep():
    car = Jeep()
    scrape(car)


class Kia(SingleCar):
    def get_name(self):
        return 'kia'


def scrapeKia():
    car = Kia()
    scrape(car)


class LandRover(SingleCar):
    def get_name(self):
        return 'land-rover'


def scrapeLandRover():
    car = LandRover()
    scrape(car)


class Lexus(SingleCar):
    def get_name(self):
        return 'lexus'


def scrapeLexus():
    car = Lexus()
    scrape(car)


class Mazda(SingleCar):
    def get_name(self):
        return 'mazda'


def scrapeMazda():
    car = Mazda()
    scrape(car)


class Mercedes(SingleCar):
    def get_name(self):
        return 'mercedes'


def scrapeMercedes():
    car = Mercedes()
    scrape(car)


class Mini(SingleCar):
    def get_name(self):
        return 'mini'


def scrapeMini():
    car = Mini()
    scrape(car)


class Mitsubishi(SingleCar):
    def get_name(self):
        return 'mitsubishi'


def scrapeMitsubishi():
    car = Mitsubishi()
    scrape(car)


class Nissan(SingleCar):
    def get_name(self):
        return 'nissan'


def scrapeNissan():
    car = Nissan()
    scrape(car)


class Opel(SingleCar):
    def get_name(self):
        return 'opel'


def scrapeOpel():
    car = Opel()
    scrape(car)


class Peugoet(SingleCar):
    def get_name(self):
        return 'peugoet'


def scrapePeugoet():
    car = Peugoet()
    scrape(car)


class Renault(SingleCar):
    def get_name(self):
        return 'renault'


def scrapeRenault():
    car = Renault()
    scrape(car)


class Saab(SingleCar):
    def get_name(self):
        return 'saab'


def scrapeSaab():
    car = Saab()
    scrape(car)


class Seat(SingleCar):
    def get_name(self):
        return 'seat'


def scrapeSeat():
    car = Seat()
    scrape(car)


class Skoda(SingleCar):
    def get_name(self):
        return 'skoda'


def scrapeSkoda():
    car = Skoda()
    scrape(car)


class Smart(SingleCar):
    def get_name(self):
        return 'smart'


def scrapeSmart():
    car = Smart()
    scrape(car)


class SsangYong(SingleCar):
    def get_name(self):
        return 'ssangyong'


def scrapeSsangYong():
    car = SsangYong()
    scrape(car)


class Subaru(SingleCar):
    def get_name(self):
        return 'subaru'


def scrapeSubaru():
    car = Subaru()
    scrape(car)


class Suzuki(SingleCar):
    def get_name(self):
        return 'suzuki'


def scrapeSuzuki():
    car = Suzuki()
    scrape(car)


class Toyota(SingleCar):
    def get_name(self):
        return 'toyota'


def scrapeToyota():
    car = Toyota()
    scrape(car)


class Volkswagen(SingleCar):
    def get_name(self):
        return 'volkswagen'


def scrapeVolkswagen():
    car = Volkswagen()
    scrape(car)


class Volvo(SingleCar):
    def get_name(self):
        return 'volvo'


def scrapeVolvo():
    car = Volvo()
    scrape(car)


class Gaz(SingleCar):
    def get_name(self):
        return 'gaz'


def scrapeGaz():
    car = Gaz()
    scrape(car)


class Moskvich(SingleCar):
    def get_name(self):
        return 'moskvich'


def scrapeMoskvich():
    car = Moskvich()
    scrape(car)


class Uaz(SingleCar):
    def get_name(self):
        return 'uaz'


def scrapeUaz():
    car = Uaz()
    scrape(car)


class Vaz(SingleCar):
    def get_name(self):
        return 'vaz'


def scrapeVaz():
    car = Vaz()
    scrape(car)


class Others(SingleCar):
    def get_name(self):
        return 'others'


def scrapeOthers():
    car = Others()
    scrape(car)
