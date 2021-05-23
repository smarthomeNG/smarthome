#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2019 Bernd Meiners                      Bernd.Meiners@mail.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG If not, see <http://www.gnu.org/licenses/>.
#########################################################################

from . import common
import unittest
import logging
import datetime

from tests.mock.core import MockSmartHome

from lib.triggertimes import Crontab

logger = logging.getLogger(__name__)

class TestCrontab(unittest.TestCase):

    def test__begin(self):
        logger.warning('')
        logger.warning('=== Begin Crontab Tests:')


    def test_zz_end(self):
        logger.warning('')
        logger.warning('=== End Crontab Tests.')

    def setUp(self):
        pass

    def test_parse(self):
        c = Crontab('0 0 * *')
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range, list(range(1,32)))
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))

        c = Crontab("@yearly")
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range,[1])
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range,[1])

        c = Crontab("@annually")
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range,[1])
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range,[1])

        c = Crontab('@monthly')
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range, [1])
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))

        c = Crontab('@weekly')
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range, list(range(1,32)))
        self.assertEqual(c.weekday_range,[0])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))

        c = Crontab('@daily')
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range, list(range(1,32)))
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))

        c = Crontab('@midnight')
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,[0])
        self.assertEqual(c.day_range, list(range(1,32)))
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))
        
        c = Crontab('@hourly')
        self.assertEqual(c.minute_range,[0])
        self.assertEqual(c.hour_range,list(range(0,24)))
        self.assertEqual(c.day_range, list(range(1,32)))
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))
        
        c = Crontab('8 * * * *')
        self.assertEqual(c.minute_range,[8])
        self.assertEqual(c.hour_range,list(range(0,24)))
        self.assertEqual(c.day_range, list(range(1,32)))
        self.assertEqual(c.weekday_range,[0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(c.second_range,[0])
        self.assertEqual(c.month_range, list(range(1,13)))

        #    self.assertEqual(parse_time_parameter(now, '0 0 * * *'), datetime.datetime(year, 1, 2, 0, 0) )

    def test_minutes(self):
    
        # something easy
        year = 2019
        month = 1
        day = 1
        hour = 12
        minute = 0
        second = 0
        now = datetime.datetime(year,month,day,hour,minute,second)

        c = Crontab('0 0 * * *')
        self.assertEqual(c.get_next(now), datetime.datetime(year, month, day+1, 0, 0) )

        now = datetime.datetime(year,month,day,hour,minute,second)
        c = Crontab('8 * * * *')
        self.assertEqual(c.get_next(now), datetime.datetime(year, month, day, 12, 8, 0) )

        year = 2019
        month = 1
        day = 1
        hour = 15
        minute = 58
        second = 50
        now = datetime.datetime(year,month,day,hour,minute,second)

        c = Crontab('*/10 */2 * * * *')
        n = c.get_next(now)
        #logger.warning(f"{now} --> {n}")
        self.assertEqual(n, datetime.datetime(year, month, day, 16, 0, 0) )
        
        year = 2019
        month = 1
        day = 1
        hour = 15
        minute = 58
        second = 50
        now = datetime.datetime(year,month,day,hour,minute,second)

        self.assertEqual(Crontab('59 12 24 12 *').get_next(now), datetime.datetime(year, 12, 24, 12, 59)) 
        self.assertEqual(Crontab('59 12 24 12 6').get_next(now), datetime.datetime(2023, 12, 24, 12, 59)) 

        logger.warning('\ncheck crontab presets')
    
        logger.warning('\ncheck crontab day substitution')
        self.assertEqual(Crontab('59 12 24 12 sun').get_next(now), datetime.datetime(2023, 12, 24, 12, 59))
        logger.warning('\n--------------------')
        self.assertEqual(Crontab('59 12 24 12 mOn').get_next(now), datetime.datetime(2029, 12, 24, 12, 59))
        logger.warning('\n--------------------')
        self.assertEqual(Crontab('59 12 24 12 Mo').get_next(now), datetime.datetime(2029, 12, 24, 12, 59)) 
        self.assertEqual(Crontab('59 12 24 12 Fri').get_next(now), datetime.datetime(2021, 12, 24, 12, 59))


        self.assertEqual(Crontab('59 23 31 12 *').get_next(now), datetime.datetime(year, 12, 31, 23, 59))
    
        self.assertEqual(Crontab('11 11 29 2 *').get_next(now), datetime.datetime(2020, 2, 29, 11, 11))
        self.assertEqual(Crontab('11 11 29 2 6').get_next(now), datetime.datetime(2032, 2, 29, 11, 11))
    
     
        year = 2019
        month = 10
        day = 31
        hour = 23
        minute = 57
        second = 00
        now = datetime.datetime(year,month,day,hour,minute,second)
        
        logger.warning('\nmore fancy dates')
        self.assertEqual(Crontab('59 23 31 10 *').get_next(now), datetime.datetime(year, 10, 31, 23, 59)) 
     
        second = 58
        now = datetime.datetime(year,month,day,hour,minute,second)
        
        logger.warning('\nfurthermore fancy dates')
        self.assertEqual(Crontab('59 23 31 10 *').get_next(now), datetime.datetime(year, 10, 31, 23, 59)) 
     
        minute = 58
        second = 0
        now = datetime.datetime(year,month,day,hour,minute,second)
        
        logger.warning('\nfurthermore fancy dates')
        self.assertEqual(Crontab('59 59 23 31 10 *').get_next(now), datetime.datetime(year, 10, 31, 23, 59, 59)) 


if __name__ == '__main__':
    unittest.main(verbosity=2)
