#/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: xiaolan_xiaobai_slot_time.py
# Author: bhb 
# Created Time: 2016-08-31 14:57:45
#########################################################################

from slotfuc_weather import *
import re
import sys
from slotfuc_weather import *
from numberfind import *
CommonNumDict = {u'〇': 0, u'O': 0, u'零': 0, u'那一': 1, u"那": 1,
        u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10, \
        u'两': 2, u'壹': 1, u'贰': 2, u'叁': 3, u'肆': 4, u'伍': 5, u'陆': 6, u'柒': 7, u'扒': 8, u'玖': 9, u'拾': 10, \
        u'十一': 11, u'十二': 12, u'十三': 13, u'十四': 14, u'十五': 15, u'十六': 16, u'十七': 17, u'十八': 18, u'十九': 19,
        u'二十': 20, \
                u'一十一': 11, u'一十二': 12, u'一十三': 13, u'一十四': 14, u'一十五': 15, u'一十六': 16, u'一十七': 17, u'一十八': 18,
                u'一十九': 19, \
                        u'二十一': 21, u'二十二': 22, u'二十三': 23, u'二十四': 24, u'二十五': 25, u'二十六': 26, u'二十七': 27, u'二十八': 28,
                        u'二十九': 29, \
                                u'三十': 30, u'三十一': 31, u"三十二": 32,u'三十三': 33, u'三十四': 34, u"三十五": 35,u'三十六': 36, u'三十七': 37, u"三十八": 38,u'三十九': 39,
                                u'四十': 40, u"四十一": 41,u'四十二': 42, u"四十三": 43,u'四十四': 44, u"四十五": 45,u'四十六': 46, u"四十七": 47,u'四十八': 48, u"四十九": 49, \
                                        u'五十': 50, u"五十一":51, u'五十二': 52, u"五十三": 53, u'五十四': 54, u"五十五": 55, u'五十六': 56, u"五十七": 57,
                                        u'五十八': 58, u"五十九": 59, \
                                                u'日': 7, u'天': 7 
                                                                 }
nf = NumberFind()

numre =u"(?:\d|一|二|两|三|四|五|六|七|八|九|十|半)"
def Numtran(hour = "",minutes = "",seconds = ""):
    if type(hour) is unicode:
        hour = hour.encode("utf-8")
    if type(minutes) is unicode:
        minutes = minutes.encode("utf-8")
    if type(seconds) is unicode:
        seconds = seconds.encode("utf-8")

    if not hour:
        hour = 0
    elif nf.numberfind(hour):
        if "半" in hour:
            hour = float(nf.numberfind(hour)[-1]) + 0.5
        else:
            hour = float(nf.numberfind(hour)[-1])
    else :
        hour = 0.5

    if not minutes:
        minutes = 0
    elif nf.numberfind(minutes):
        if "刻" in minutes:
            minutes = float(nf.numberfind(minutes)[-1]) * 15
        else:
            minutes = float(nf.numberfind(minutes)[-1])
    else :
        if "分" not in minutes and "半" in minutes:
            minutes = 30 
        elif "分" in minutes and "半" in minutes:
            minutes = 0.5
        elif "刻" in minutes and "半" in minutes:
            minutes = 15 * 0.5

    if not seconds:
        seconds = 0
    else :
        seconds = float(nf.numberfind(seconds)[-1])

    return hour , minutes, seconds
    

def TimeTrans1(query, timestr):
    timestr = timestr.strip()
    daysnums,date = DateTrans(query)
    #print daysnums ,date

    matchobj = re.search(u"(中午|明早|傍晚|凌晨|下午|晚上|上午|早上)?(?:(" + numre + u"{1,3})(?:点|时|\:))(?:((?:过){0,1}?" + numre + u"{1,3}(?:分|刻钟|分钟|钟|刻|\:){0,1})){0,1}(?:(" + numre + u"{1,3}(?:秒|秒钟|\:){0,1})){0,1}",timestr)
    #print matchobj.groups()
    if not matchobj:
        return None,None
    #print type(matchobj.group()),"TimeTrans1"
    tag ,hour ,minutes ,seconds =  matchobj.groups()
    #print tag ,hour ,minutes ,seconds
    hour ,minutes ,seconds = Numtran(hour ,minutes ,seconds )
    #print hour ,minutes ,seconds

    hour = int(hour)
    minutes = int(minutes)
    seconds = int(seconds)

    nowobj = time.localtime()
    nowhour = nowobj.tm_hour
    nowmin = nowobj.tm_min
    nowsec = nowobj.tm_sec

    if tag in [u"下午",u"晚上",u"傍晚"]:
        #date = date + datetime.timedelta(days = 1)
        if hour < 12:
            return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour + 12 ,minutes ,seconds)
        else :
            return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)

    if daysnums == 0:


        if tag in [u"凌晨",u"明早",u"早上"]:
            date = date + datetime.timedelta(days = 1)
            return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)

        if hour == nowhour:
            if nowmin > minutes:
                date = date + datetime.timedelta(days = 1)
                return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)
            elif nowmin == minutes:
                if nowsec > seconds:
                    date = date + datetime.timedelta(days = 1)
                    return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)
                else :
                    return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)
            else:
                return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)

        if hour < nowhour and (hour + 12) < nowhour:
            date = date + datetime.timedelta(days = 1)
            return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)

        if hour < nowhour and (hour + 12) >  nowhour and hour < 12:
            hour = hour + 12
            return matchobj.group() ,datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)

    return matchobj.group() ,  datetime.datetime(date.year, date.month ,date.day ,hour ,minutes ,seconds)
    

    #return date + datetime.timedelta(days = 1)
def TimeTrans2(query, timestr):
    timestr = timestr.strip()
    daysnums,date = DateTrans(query)
    #if re.search(u"(?:中餐|早餐|午餐|晚餐|早饭|午饭|晚饭|睡觉|起床)(?:时|的时候|时候)")
    if re.search(u"(?:早餐|早饭)(?:时|的时候|时候){0,1}",timestr):
        return re.search(u"(?:早餐|早饭)(?:时|的时候|时候){0,1}",timestr).group(),datetime.datetime(date.year, date.month ,date.day ,7 ,0 ,0)
    if re.search(u"(?:中餐|午饭|午餐)(?:时|的时候|时候){0,1}",timestr):
        return re.search(u"(?:中餐|午饭|午餐)(?:时|的时候|时候){0,1}",timestr).group(),datetime.datetime(date.year, date.month ,date.day ,12 ,0 ,0)
    if re.search(u"(?:晚餐|晚饭)(?:时|的时候|时候){0,1}",timestr):
        return re.search(u"(?:晚餐|晚饭)(?:时|的时候|时候){0,1}",timestr).group(),datetime.datetime(date.year, date.month ,date.day ,19 ,0 ,0)
    
    return None , None

def Isintimetag(timetag):
    if not timetag:
        return False
    for t in [u"后的",u"后面的",u"以后",u"前",u"之前",u"之后",u"之后",u"后"]:
        if timetag.find(t) != -1:
            return True

    for t in [u"前",u"之前"]:
        if timetag.find(t) != -1:
            return -1

    for t in [u"后的",u"后面的",u"以后",u"之后",u"之后",u"后"]:
        if timetag.find(t) != -1:
            return 1
    
    return False

def TimeTrans3(query, timestr):
    hourall = 0
    minall = 0
    secall = 0
    timestr = timestr.strip()
    daysnums,date = DateTrans(query)
    #hourmidstr = u"(?:" + numre + u"{1,3}(?:点" + numre + u"{1,3}){0,1}(?:个|半){0,2}小时)"
    #minmidstr = u"(?:" + numre + u"{1,3}(?:分钟|刻钟|分|钟|刻))"
    #secmidstr = u"(?:" + numre + u"{0,3})(?:秒|秒钟))"

    #complair1 =hourmidstr + minmidstr + secmidstr 
    #complair1 =minmidstr + secmidstr 
    #complair1 =secmidstr 
    matchobj1 = re.search(u"(后的|后面的|以后|前|之前|之后|后)(?:.{0,2}?)(?:(" + numre + u"{1,3}(?:(?:\.|点)" + numre + u"{1,3}){0,1}(?:个|半){0,2})小时){0,1}(?:(" + numre + u"{1,3}(?:分|分钟|刻钟|钟|刻))){0,1}(?:(" + numre + u"{0,3})(?:秒|秒钟)){0,1}",timestr)
    matchobj2 = re.search(u"(?:(" + numre + u"{1,3}(?:(?:\.|点)" + numre + u"{1,3}){0,1}(?:个|半){0,2})小时){0,1}(?:(" + numre + u"{1,3}(?:分|分钟|钟|刻钟|刻))){0,1}(?:(" + numre + u"{0,3})(?:秒|秒钟)){0,1}(后面|后面的|以后|后|前|之前|之后)",timestr)

    matchobj =None
    
    #print nf.numberfind(matchobj2.group()),"--------->nf.numberfind(matchobj2.group())"
    if not matchobj1 and not matchobj2:
        return None
    elif nf.numberfind(matchobj1.group().encode("utf-8")):
        matchobj = matchobj1
    #elif len(matchobj1.group()) <  len(matchobj2.group()):
        #print len(matchobj1.group()) , len(matchobj2.group())
    elif nf.numberfind(matchobj2.group().encode("utf-8")):
        matchobj = matchobj2
    else:
        matchobj = matchobj1
    #print matchobj.group()
    if not matchobj:
        return None
    #print matchobj.groups(),"TimeTrans2"
    t1 ,t2, t3 ,t4  =matchobj.groups()
    #print matchobj.groups()
    #print t1 ,t2, t3 ,t4
    #print t1 ,t2, t3 ,t4
    #print type(t1)
    
    #if t4 in [u"后的",u"后面的",u"以后",u"前",u"之前",u"之后",u"之后",u"后"]:
    if Isintimetag(t4):
        hours ,mins ,secs = Numtran(t1 ,t2, t3)
        if Isintimetag(t4) == 1:
            hourall += hours
            minall += mins
            secall += secs
        if Isintimetag(t4) == -1:
            hourall -= hours
            minall -= mins
            secall -= secs

    elif Isintimetag(t1):
        hours ,mins ,secs = Numtran(t2, t3 ,t4)
        if Isintimetag(t1) == 1:
            hourall += hours
            minall += mins
            secall += secs
        if Isintimetag(t1) == -1:
            hourall -= hours
            minall -= mins
            secall -= secs

    
        

    #matchobjs = re.findall(u"((?:后的|后面的|前|之前|之后|后){0,1}(?:.{0,2}?)(?:(?:" + numre + u"{1,3}(?:点" + numre + u"{1,3}){0,1}(?:个|半){0,2}小时)){0,1}(?:(?:" + numre + u"{1,3}(?:分钟|刻钟|分|钟|刻))){0,1}(?:(?:" + numre + u"{0,3})(?:秒|秒钟)){0,1}(?:后|前|之前|之后){0,1})",timestr)
    #if not matchobjs:
    #    return None
    #for matchobj in matchobjs:
    #    if matchobj:
    #        print "matchobj---->",matchobj
    #        matchobj = re.search(u"(后的|后面的|后|前|之前|之后){0,1}(?:.{0,2}?)(?:(" + numre + u"{1,3}(?:点" + numre + u"{1,3}){0,1}(?:个|半){0,2})小时){0,1}(?:(" + numre + u"{1,3}(?:分|分钟|钟|刻))){0,1}(?:(" + numre + u"{0,3})(?:秒|秒钟)){0,1}(后|前|之前|之后|以后){0,1}",matchobj)
    #        if matchobj:
    #            print matchobj.groups(),"TimeTrans2"
    #            tag1,hours ,mins ,secs ,tag2 =matchobj.groups()
    #            print tag1 ,hours ,mins ,secs ,tag2
    #            hours ,mins ,secs = Numtran(hours ,mins ,secs)
    #            print hours,mins,secs
    #            tags = [tag1,tag2]
    #            #print tags
    #            for t in tags:
    #                if t:
    #                    if t in [u"后的",u"后面的",u"之后",u"后",u"以后"] :
    #                        hourall += hours
    #                        minall += mins
    #                        secall += secs
    #                    if t in [u"之前",u"前"]:
    #                        hourall -= hours
    #                        minall -= mins
    #                        secall -= secs
    spaceseconds = hourall * 3600 + minall *60 + secall
    #print spaceseconds


    daysnums,date = DateTrans(timestr)
    nowobj = time.localtime()
    nowhour = nowobj.tm_hour
    nowmin = nowobj.tm_min
    nowsec = nowobj.tm_sec
    finalltime = datetime.datetime(date.year ,date.month ,date.day ,nowhour ,nowmin ,nowsec) + datetime.timedelta(seconds = spaceseconds)          
    #print finalltime
    return finalltime

def Difftime(datetimestr):
    nowdate = datetime.datetime.now()
    nowday = nowdate.day
    nowobj = time.localtime()
    nowhour = nowobj.tm_hour
    nowmin = nowobj.tm_min
    nowsec = nowobj.tm_sec

    reday = datetimestr.day
    rehour = datetimestr.hour
    reminute = datetimestr.minute
    resecond = datetimestr.second
    difftimesecond = (reday - nowday) * 86400 + (rehour - nowhour) * 3600 + (reminute - nowmin) * 60 + (resecond - nowsec)
    return difftimesecond

def Difftime2time(seconds):
    nowdate = datetime.datetime.now()
    nowyear = nowdate.year
    nowmonth = nowdate.month
    nowday = nowdate.day

    nowobj = time.localtime()
    nowhour = nowobj.tm_hour 
    nowmin = nowobj.tm_min
    nowsec = nowobj.tm_sec

    finalltime = datetime.datetime(nowyear, nowmonth, nowday, nowhour, nowmin, nowsec) + datetime.timedelta(seconds = seconds)
    return finalltime
                         
def Slottimefind(queryobj):
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj
    timestr = query
    secondsall = 0
    matchobj = re.search(u"(中午|明早|傍晚|凌晨|下午|晚上|上午|早上)?(?:(" + numre + u"{1,3})(?:点|时|\:))(?:((?:过){0,1}?" + numre + u"{1,3}(?:分|刻钟|分钟|钟|刻|\:){0,1})){0,1}(?:(" + numre + u"{1,3}(?:秒|秒钟|\:){0,1})){0,1}",timestr)

    matchstrt1 = ""
    matchtime1 = None
    if not matchobj:
        timestr = timestr
    else:
        timestr = timestr[timestr.find(matchobj.group()):]
    matchstrt1 , matchtime1 = TimeTrans1(query, timestr)
    #print "matchstrt1--->",matchstrt1 , "matchtime1-->",matchtime1
    if not matchstrt1:
        timestr = timestr
    else :
        timestr = re.sub(matchstrt1,'',timestr)
    #print "timestr1--->",timestr
    matchstrt2 ,matchtime2 = TimeTrans2(query, timestr)
    #print "matchtstr2--->",matchstrt2,"matchtime2-->",matchtime2
    if not matchstrt2:
        timestr = timestr
    else :
        timestr = timestr[(timestr.find(matchstrt2) + len(matchstrt2)):]
        timestr = re.sub(matchstrt2,'',timestr)
    #print "timestr2--->",timestr
    matchtime3 = TimeTrans3(query, timestr)
    if not matchtime1 and not matchtime2 and not matchtime3:
        return None
    datetimelst = [matchtime1,matchtime2,matchtime3]
    #print datetimelst,'----------'
    for t in datetimelst:
        if t:
            secondsall += Difftime(t)
    finalldatetime = Difftime2time(secondsall)
    print finalldatetime
    return {"Time":str(finalldatetime)}
                                                                                                                                                                         








if __name__=="__main__":
    for line in sys.stdin:
        line = line.strip().decode("utf-8")
        #line = line.strip()
        print line,"  -->   ",Slottimefind(line), "\n"
        #print TimeTrans2(line)
        #print Difftime(line)
