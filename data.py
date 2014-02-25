# -*- coding: utf-8 -*-

from datetime import date, time
from pytz import timezone


'''week_start and week_data ONLY FOR 2013-2014 first semester, should be updated every semester.
'''

# date of the first Monday
week_start = date(2013, 9, 9)

week_data = {
    u"秋": {
        "odd":  [1, 3, 6, 8],
        "even": [2, 5, 7, 9],
        "all":  [1, 2, 3, 5, 6, 7, 8, 9],
    },
    u"冬": {
        "odd":  [11, 13, 15, 17],
        "even": [12, 14, 16, 18],
        "all":  [11, 12, 13, 14, 15, 16, 17, 18],
    },
    u"秋冬": {
        "odd":  [1, 3, 6, 8, 11, 13, 15, 17],
        "even": [2, 5, 7, 9, 12, 14, 16, 18],
        "all":  [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18],
    },
}


def time_shanghai(h, m):
    return time(h, m, tzinfo=timezone('Asia/Shanghai'))

lesson_time = [
    {},
    {
        "start": time_shanghai(8, 0),
        "end": time_shanghai(8, 45),
    },
    {
        "start": time_shanghai(8, 50),
        "end": time_shanghai(9, 35),
    },
    {
        "start": time_shanghai(9, 50),
        "end": time_shanghai(10, 35),
    },
    {
        "start": time_shanghai(10, 40),
        "end": time_shanghai(11, 25),
    },
    {
        "start": time_shanghai(11, 30),
        "end": time_shanghai(12, 15),
    },
    {
        "start": time_shanghai(13, 15),
        "end": time_shanghai(14, 0),
    },
    {
        "start": time_shanghai(14, 5),
        "end": time_shanghai(14, 50),
    },
    {
        "start": time_shanghai(14, 55),
        "end": time_shanghai(15, 40),
    },
    {
        "start": time_shanghai(15, 55),
        "end": time_shanghai(16, 40),
    },
    {
        "start": time_shanghai(16, 45),
        "end": time_shanghai(17, 30),
    },
    {
        "start": time_shanghai(18, 30),
        "end": time_shanghai(19, 15),
    },
    {
        "start": time_shanghai(19, 20),
        "end": time_shanghai(20, 5),
    },
    {
        "start": time_shanghai(20, 10),
        "end": time_shanghai(20, 55),
    },
]
