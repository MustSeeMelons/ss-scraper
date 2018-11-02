import sys
import time
import platform
import datetime

if sys.platform == 'win32':
    default_timer = time.perf_counter
else:
    default_timer = time.time

start = 0


def startTimer():
    start = default_timer()


def endTimer():
    end = default_timer()
    elapsed = (end - start) * 1000 * 1000
    print("Runtime: {:.2f}".format(elapsed) + " ns")


class Sanitizer:
    @staticmethod
    def sanitizePrice(price):
        if price == None:
            return price
        else:
            split = price.split()
            if len(split) == 1:
                try:
                    int(split[0])
                    return split[0]
                except:
                    return None
            else:
                return "".join(split[:-1])

    @staticmethod
    def sanitizeDate(date):
        if date == None:
            return date
        else:
            split = date.split()
            if len(split) == 1:
                try:
                    int(split[0])
                    return split[0]
                except:
                    return None
            else:
                return split[0]

    @staticmethod
    def sanitizeInspection(inspection):
        if inspection == None:
            return inspection
        else:
            split = inspection.split('.')
            if len(split) == 1:
                return None

            if split[0] == '0' or split[1] == '0':
                return None

            year = int(split[0]) if int(split[0]) > int(
                split[1]) else int(split[1])
            month = int(split[1]) if int(split[0]) > int(
                split[1]) else int(split[0])

            return datetime.datetime(year=year, month=month, day=1).strftime('%Y-%m-%d')
            
            

    @staticmethod
    def sanitizeMileage(mileage):
        if mileage == None:
            return mileage
        else:
            split = mileage.split()
            if len(split) == 1:
                return float(split[0])
            else:
                return float("".join(split))

    @staticmethod
    def isCarValid(make, price, ta):
        if make != None and price != None and ta != None:
            return True
        return False
