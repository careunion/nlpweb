#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: test.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-16 11:11:23
#########################################################################

import urllib
import urllib2
import  xml.dom.minidom
import xml.etree.ElementTree as ET 
import re
import time
import datetime
import os

pwd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

TagnameDict = {}
CommonNumDict = {u'〇':0, u'O':0, u'零':0, u'那一':1, u"那":1, 
           u'一':1, u'二':2, u'三':3, u'四':4, u'五':5, u'六':6, u'七':7, u'八':8, u'九':9, u'十':10,\
                   u'两':2, u'壹':1, u'贰':2, u'叁':3, u'肆':4, u'伍':5, u'陆':6, u'柒':7, u'扒':8,u'玖':9, u'拾':10, \
            u'十一':11, u'十二':12, u'十三':13, u'十四':14, u'十五':15, u'十六':16, u'十七':17, u'十八':18, u'十九':19, u'二十':20,\
            u'一十一':11, u'一十二':12, u'一十三':13, u'一十四':14, u'一十五':15, u'一十六':16, u'一十七':17, u'一十八':18, u'一十九':19,\
            u'二十一':21, u'二十二':22, u'二十三':23, u'二十四':24, u'二十五':25, u'二十六':26, u'二十七':27, u'二十八':28, u'二十九':29,\
            u'三十':30, u'三十一':31,\
            u'日':7, u'天':7
                }
CommonDayDict = {u"今天":0, u"明天":1, u"昨天":-1, u"前天":-2, u"大前天":-3, u"后天":2, u"大后天":3        }

def dataload(filepath, _dict):
    for line in open(filepath):
        infos = line.strip().decode("utf-8").split()
        if len(infos) != 2:
            continue
        _dict[infos[0]] = infos[1]

def WeatherUrl(city, day):
    if day < 0 or day > 4:
        return None
    urlpre = "http://php.weather.sina.com.cn/xml.php?"
    urlmid = "&password=DJOYnieT8234jlsK&"

    if type(city) is unicode:
        city = city.encode("gb2312")

    cityinfo = {"city": city}
    dayinfo = {"day" : day}

    citystr = urllib.urlencode(cityinfo)
    daystr = urllib.urlencode(dayinfo)

    requrl = urlpre + citystr + urlmid + daystr

    req = urllib2.Request(requrl)
    res = urllib2.urlopen(req)
    xmlstr = res.read()

    rootnode = ET.fromstring(xmlstr).getchildren()
    if not rootnode:
        return None
    nodes = rootnode[0].getchildren()
    _dict = {}
    for node in nodes:
        if node.tag not in TagnameDict:
            continue
        _dict[TagnameDict[node.tag] ] = node.text
    return _dict

def DateTrans1(datestr):
    matchobj = re.search(u"(上|下|前|后)?(一|二|两|三|四|五|六|七|八|九)?(?:个)?(?:周|礼拜)", datestr)
    if not matchobj:
        return None
    postive, num = matchobj.groups()
    if not num: num = 1
    else:num = CommonNumDict[num]
    if postive in u"上前":postive = -1
    elif postive in u"下后":postive = 1
    return postive * 7 * num

def DateTrans2(datestr):
    matchobj = re.search(u"(?:周|礼拜)(一|二|两|三|四|五|六|七|日|天)", datestr)
    if not matchobj:
        return None
    num = CommonNumDict[matchobj.groups()[0]]
    today = time.gmtime().tm_wday + 1
    return num - today 

def DateTrans3(datestr):
    matchobj = re.findall(u"(今天|明天|昨天|前天|大前天|后天|大后天)", datestr)
    num = 0
    for matchstr in matchobj:
        num += CommonDayDict[matchstr]
    return num

def DateTrans4(datestr):
    matchobj = re.search(u"((?:\d|一|二|两|三|四|五|六|七|八|九|十){1,3})天.{0,2}(前|后)", datestr)
    if not matchobj:
        return None
    postive = matchobj.groups()[1]
    num = matchobj.groups()[0]
    if postive in u"前":postive = -1
    elif postive in u"后":postive = 1
    if not num.isdigit():
        num = CommonNumDict[num]
    else:
        num = int(num)
    return postive * num

def DateTrans5(datestr):
    matchobj = re.search(u"(?:(上|下|前|后)?(一|二|两|三|四|五|六|七|八|九|十|十一|十二)?(?:个)?(?:月)(前|后)?)?.{0,3}?(?:((?:\d|一|二|三|四|五|六|七|八|九|十)*)(?:号|日))?", datestr)

    nowobj = time.gmtime()
    year = nowobj.tm_year
    month = nowobj.tm_mon
    day = nowobj.tm_mday

    postive1, monthnum, postive2, daynum = matchobj.groups()

    if postive1 or postive2:
        if not monthnum: monthnum = 1
        else: monthnum = CommonNumDict[monthnum]
        postive = 1
        if  (postive1 and postive1 in u"上前") or (postive2 and postive2 in u"上前"):
            postive = -1
        month = month + postive * monthnum
    else:
        if monthnum:
            month = CommonNumDict[monthnum]
    if daynum:
        day = CommonNumDict[daynum]
    
    yearstep = month/12
    year = year + yearstep
    month = month%12
    
    newdatetime = datetime.datetime(year, month, day, 0, 0, 0)
    nowdatetime = datetime.datetime.now()
    return (newdatetime - nowdatetime).days + 1



def DateTrans(datestr):
    fus = [DateTrans1, DateTrans2, DateTrans3, DateTrans4, DateTrans5]
    days = [fuc(datestr) for fuc in fus]
    daynums = [t for t in days if t]
    dayrange = sum(daynums)

    if(dayrange < 0):
        n = abs(dayrange)
        return dayrange, datetime.date.today() - datetime.timedelta(days=n)
    else:
        return dayrange, datetime.date.today() + datetime.timedelta(days=dayrange)


dataload(pwd_path + "/data/tagname.dat", TagnameDict)
