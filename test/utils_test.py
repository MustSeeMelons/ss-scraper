import sys
sys.path.append("..")

import datetime
import unittest
from utils.utils import Sanitizer

time_format = '%Y-%m-%d'

class UtilsTest(unittest.TestCase):
    def testDefaultCasePrice(self):
        self.assertEqual(Sanitizer.sanitizePrice('5000 $'), '5000')

    def testEmptyPrice(self):
        self.assertEqual(Sanitizer.sanitizePrice(None), None)

    def testOtherValuePrice(self):
        self.assertEqual(Sanitizer.sanitizePrice('abc'), None)

    def testAlreadyGoodValuePrice(self):
        self.assertEqual(Sanitizer.sanitizePrice('500'), '500')

    def testHugeValuePrice(self):
        self.assertEqual(Sanitizer.sanitizePrice('25 000 $'), '25000')

    def testDefaultCaseDate(self):
        self.assertTrue(Sanitizer.sanitizeDate('2008 aprīlis'), '2008')

    def testEmptyDate(self):
        self.assertEqual(Sanitizer.sanitizeDate(None), None)

    def testOtherValueDate(self):
        self.assertEqual(Sanitizer.sanitizeDate('abc'), None)

    def testAlreadyGoodValueDate(self):
        self.assertEqual(Sanitizer.sanitizeDate('2008'), '2008')

    def testDefaultCaseInspection(self):
        self.assertEqual(Sanitizer.sanitizeInspection('10.2019'),  datetime.datetime(year=2019, month=10, day=1).strftime(time_format))

    def testReverseCaseInspection(self):
        self.assertEqual(Sanitizer.sanitizeInspection('2019.10'),  datetime.datetime(year=2019, month=10, day=1).strftime(time_format))

    def testFaultyCaseInspection(self):
        self.assertEqual(Sanitizer.sanitizeInspection('None'), None)

    def testDefaultValueMiles(self):
        self.assertEqual(Sanitizer.sanitizeMileage('111 222'), 111222)

    def testAlreadyGoodValueMiles(self):
        self.assertEqual(Sanitizer.sanitizeMileage('111222'), 111222)


if __name__ == '__main__':
    unittest.main()