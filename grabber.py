#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os.path
import re
import getpass
from bs4 import BeautifulSoup, SoupStrainer
from helpers import pretty_format, chinese_weekdays

# data for fake login
USERNAME = ''
COOKIES = {'ASP.NET_SessionId': ""}

# weeks data ONLY FOR 2012-2013 second semester, should be updated every semester
week_data = {
    u"春": {
        "odd":  [1, 3, 5, 7],
        "even": [2, 4, 6, 8],
        "all":  [1, 2, 3, 4, 5, 6, 7, 8],
    },
    u"夏": {
        "odd":  [10, 12, 14, 16],
        "even": [11, 13, 15, 17],
        "all":  [10, 11, 12, 13, 14, 15, 16, 17],
    },
    u"春夏": {
        "odd":  [1, 3, 5, 7, 10, 12, 14, 16],
        "even": [2, 4, 6, 8, 11, 13, 15, 17],
        "all":  [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17],
    },
}

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

    def _fetch_img(self):
        url_captcha = self.url_prefix + "CheckCode.aspx"
        r = requests.get(url_captcha)
        self.captcha_img = r.content
        self.cookies = r.cookies

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
        self._fetch_img()
        with open(os.path.join(os.path.dirname(__file__), 'img.gif'), 'w') as img:
            img.write(self.captcha_img)

        self.username = raw_input('Username: ')
        self.password = getpass.getpass('Password: ')
        self.captcha = raw_input('Captcha: ')

    def _fake_login(self):
        self.username = USERNAME
        self.cookies = COOKIES

    def _login(self):
        self._setup()
        url_login = self.url_prefix + "default2.aspx"
        data = {
            'TextBox1': self.username,
            'TextBox2': self.password,
            'Textbox3': self.captcha,
            'RadioButtonList1': u'学生'.encode(self.charset),
            '__EVENTTARGET': "Button1",
            '__EVENTARGUMENT': "",
            '__VIEWSTATE': "dDwtMTAzMjcxNTk2NDs7Pl+gyMxRYhv1lADUeH98zifgfUbl",
            'Text1': "",
        }
        r_login = requests.post(url_login, data=data, cookies=self.cookies)

        result = re.match("<script language='javascript'>alert\('(.{,300})'\);</script>", r_login.content)
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
            raise LoginError("unknown")
        print "Logged in successfully."

        self.cookies = r_login.cookies

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
            if r.has_key('class') and r['class'] == ["datagridhead"]:
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

if __name__ == "__main__":
    grabber = TeapotParser()
    try:
        response = grabber.run()
    except LoginError as e:
        print 'Login error: ' + e.error
    except:
        raise
    else:
        with open(os.path.join(os.path.dirname(__file__), 'dump.yaml'), 'w') as log:
            log.write(pretty_format(response))
