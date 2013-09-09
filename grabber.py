#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import os.path
import re
import getpass
from datetime import timedelta, datetime
from bs4 import BeautifulSoup, SoupStrainer
from icalendar import Calendar, Event
from uuid import uuid1
from helpers import pretty_format, chinese_weekdays, unify_brackets
from data import *

# for fake login
USERNAME = ''
COOKIES = {'ASP.NET_SessionId': ""}

class _Misc(object):
    pass
_misc = _Misc()

class LoginError(Exception):
    '''raise LoginError if error occurs in login process.
    '''
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'LoginError: {}'.format(self.error)


class GrabError(Exception):
    '''raise GrabError if error occurs in grab process.
    '''
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return 'GrabError: {}'.format(self.error)


class TeapotParser():
    """Parser for Zhejiang University.
    """
    def __init__(self):
        self.url_prefix = "http://jwbinfosys.zju.edu.cn/"
        self.charset = "gbk"

    def get_semester_from_time(self, time_text):
        if u"秋冬" in time_text:
            return u"秋冬"
        elif u"秋" in time_text:
            return u"秋"
        elif u"冬" in time_text:
            return u"冬"
        elif u"春夏" in time_text:
            return u"春夏"
        elif u"春" in time_text:
            return u"春"
        elif u"夏" in time_text:
            return u"夏"
        else:
            return None

    @staticmethod
    def parse_odd_or_even(text):
        if u"单" in text:
            return "odd"
        elif u"双" in text:
            return "even"
        else:
            return "all"

    @staticmethod
    def trim_location(l):
        l = l.replace(u"(多媒体，音乐教室)", "")
        l = l.replace(u"(科创专用教室)", "")
        l = l.replace(u"(网络五边语音)", "")
        l = l.replace(u"(网络五边菱)", "")
        l = l.replace(u"(长方无黑板)", "")
        l = l.replace(u"(五边菱形)", "")
        l = l.replace(u"(六边圆形)", "")
        l = l.replace(u"(网络六边)", "")
        l = l.replace(u"(网络五边)", "")
        l = l.replace(u"(传统语音)", "")
        l = l.replace(u"(长方形)", "")
        l = l.replace(u"(语音)", "")
        l = l.replace(u"(成多)", "")
        l = l.replace(u"(普)", "")
        l = l.replace(u"(多)", "")
        l = l.replace("*", "")
        return l

    def get_lessons(self, time_texts, locations, semester_text):
        '''parse lesson'''
        ''' - parse time'''
        lessons = []
        for time_text in time_texts:
            '''parse week'''
            odd_or_even = self.parse_odd_or_even(time_text)

            '''sometimes, lesson has its own semester text'''
            semester = self.get_semester_from_time(time_text)
            if semester:
                weeks = week_data[semester][odd_or_even]
            else:
                weeks = week_data[semester_text][odd_or_even]

            number = re.findall("\d{1,2}", time_text[3:])
            if time_text:
                weekday = re.search(u"周(.)", time_text).group(1)
                lessons.append({
                    'day': chinese_weekdays[weekday],
                    'start': int(number[0]),
                    'end': int(number[-1]),
                    'weeks': weeks,
                })
            else:
                lessons.append({})

        ''' - parse location'''
        locations = map(self.trim_location, locations)
        if len(locations) > 1:
            '''each lesson has different location'''
            for i in range(len(lessons)):
                if lessons[i]:
                    try:
                        lessons[i]['location'] = locations[i]
                    except IndexError:
                        pass
        elif len(locations) == 1:
            '''lessons share the same location'''
            for l in lessons:
                if l:
                    l['location'] = locations[0]

        lessons = filter(bool, lessons)

        '''deal w/ special case: one lesson separated to two'''
        lessons = sorted(lessons, key=lambda x: (x['day'], x['start']))
        for i in range(1, len(lessons)):
            if (lessons[i]['day'] == lessons[i - 1]['day'] and
               lessons[i]['start'] == lessons[i - 1]['end'] + 1 and
               lessons[i]['location'] == lessons[i - 1]['location']):
                lessons[i - 1]['end'] = lessons[i]['end']
                lessons[i]['delete'] = True
        lessons = filter(lambda x: 'delete' not in x, lessons)

        return lessons

    def _setup(self):
        #self.username = raw_input('Username: ')
        #self.password = getpass.getpass('Password: ')
        self.username = _misc.username
        self.password = _misc.password

    def _get_cookies(self):
        url_default = self.url_prefix + "default2.aspx"
        r_defaults = requests.get(url_default)
        self.cookies = r_defaults.cookies

    def _fake_login(self):
        self.username = USERNAME
        self.cookies = COOKIES

    def _login(self):
        self._setup()
        self._get_cookies()
        url_login = self.url_prefix + "default2.aspx"
        data = {
            'TextBox1': self.username,
            'TextBox2': self.password,
            'Textbox3': "",
            'RadioButtonList1': u'学生'.encode(self.charset),
            '__EVENTTARGET': "Button1",
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': "dDwxOTEwMzI3NDAyOzs+hurYK255qc/CsDx7/bCGtJreiuI=",
            'Text1': "",
        }
        r_login = requests.post(url_login, data=data, cookies=self.cookies)

        result = re.match(
            "<script language='javascript'>alert\('(.{,300})'\);</script>", r_login.content)
        if result:
            msg = result.group(1).decode(self.charset)
            if msg == u"验证码不正确！！":
                raise LoginError("captcha")
            if msg == u"用户名不存在！！":
                raise LoginError("auth")
            if msg[:4] == u"密码错误":
                raise LoginError("auth")
        content = r_login.content.decode(self.charset)
        if u"欢迎您来到现代教务管理系统！" not in content:
            with open(os.path.join(os.path.dirname(__file__), 'error.html'), 'w') as log:
                log.write(r_login.content)
            raise LoginError("unknown")
        print "Logged in successfully."

    def run(self):
        if USERNAME:
            self._fake_login()
        else:
            self._login()

        url_course = self.url_prefix + "xskbcx.aspx?xh=" + self.username
        r_course = requests.get(url_course, cookies=self.cookies)

        '''parse'''
        if u"调查问卷".encode(self.charset) in r_course.content:
            raise GrabError("无法抓取您的课程，请先填写教务网调查问卷。")
        strainer = SoupStrainer("table", id="xsgrid")
        soup = BeautifulSoup(r_course.content, parse_only=strainer)
        rows = soup.select("tr")
        courses = []
        for r in rows:
            if r.has_attr('class') and r['class'] == ["datagridhead"]:
                continue

            cols = r.select("td")
            semester_text = cols[3].get_text(strip=True)
            time_texts = [text for text in cols[4].stripped_strings]
            locations = [text for text in cols[5].stripped_strings]

            lessons = self.get_lessons(time_texts, locations, semester_text)

            course = {
                'original_id': cols[0].get_text(strip=True),
                'name': cols[1].get_text(strip=True),
                'teacher': cols[2].get_text(strip=True),
                'lessons': lessons,
            }
            courses.append(course)
        return courses


def gen_ical(courses):
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//Zhejiang University//LIU Dongyuan//ZH'  # *mandatory elements* where the prodid can be changed, see RFC 5445

    for course in courses:
        for lesson in course['lessons']:
            weeks = lesson['weeks']
            for recur in weeks:
                event = Event()
                event.add('summary', unify_brackets(course['name']))
                offset_days = lesson['day'] - 1 + 7 * (int(recur) - 1)
                offset = timedelta(days=offset_days)
                classdate = week_start + offset
                start = lesson_time[lesson['start']]['start']
                end = lesson_time[lesson['end']]['end']
                event.add('dtstart', datetime.combine(classdate, start))
                event.add('dtend', datetime.combine(classdate, end))
                event.add('location', lesson['location'])
                event.add('description', u'教师：' + course['teacher'])
                event['uid'] = str(uuid1()) + '@ZJU'
                cal.add_component(event)
    return cal.to_ical()

def main():
    if len(sys.argv) < 3:
        print('usage: %s username password [output_file]')
        return
    _misc.username = sys.argv[1]
    _misc.password = sys.argv[2]
    try: 
        _misc.output_file = sys.argv[3]
    except:
        _misc.output_file = '%s.ics' %sys.argv[1]
        
    grabber = TeapotParser()
    try:
        response = grabber.run()
    except LoginError as e:
        print 'Login error: ' + e.error
    except:
        raise
    else:
        #with open(os.path.join(os.path.dirname(__file__), 'dump.yaml'), 'w') as log:
        #    log.write(pretty_format(response))
        with open(os.path.join(os.path.dirname(__file__), _misc.output_file), 'w') as log:
            log.write(gen_ical(response))
        print "Dumped successfully."

if __name__ == "__main__":
    main()
