#/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: zhekou.py
# Author: bhb 
# Created Time: 2016-08-22 10:25:39
#########################################################################

import re
import sys
from numberfind import NumberFind

reload(sys)
sys.setdefaultencoding("utf-8")

Numre = u"(?:一|二|三|四|五|六|七|八|九|十|\d)"
Scope = u"(?:左右|上下|以下|小于|大于|之内|以上|以内|不到|以外)"
Nf = NumberFind()

def Slotdiscountfind(queryobj):
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj

    query = query.strip()
    focusstr = u"折扣|折"
    focuswordlist = focusstr.split("|") 
    focuswords = u"(?:" + focusstr + ")" 

    matchobjs = []
    matchobj1 =re.findall("(" + Numre + u"{1,10}(?:.{1,3})" + Numre +  u"{1,10}.*?" + focuswords + ")",query)
    matchobj2 =re.findall("(" + focuswords + u"(?:.{,3})" + Numre + u"{1,10}(?:.{1,3})" + Numre + u"{1,10}" + ")",query)
    matchobj3 =re.findall("(" + Scope + "{0,1}" + u"(?:(?:" + Numre + u"{1,10}.*?" + focuswords + ")|(?:" + focuswords + ".*?" + Numre + "{1,10}))" + ".{0,3}"+ Scope + "{0,1}" + Numre + "{0,10}" + ")",query)
    matchobj4 =re.findall(u"(" + focuswords + ")",query)
        
    matchobjs.append(matchobj4)
    matchobjs.append(matchobj3)
    matchobjs.append(matchobj2)
    matchobjs.append(matchobj1)


    result = {}
    matchobjs = [t[-1] for t in matchobjs if t]
    matchobjs = sorted(matchobjs, key=lambda x:len(x))
    for matchobj in matchobjs:
        if matchobj:
            matchres = matchobj.strip().encode("utf-8")
            number = Nf.numberfind(matchres)
            result = Slotxboperate(number,10, matchres, focuswords)
    if result:
        return {"discount":result}
    return None

def Slotreputationfind(queryobj):
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj

    query = query.strip()
    focusstr = u"信用|信用度|诚信"
    focuswordlist = focusstr.split("|") 
    focuswords = u"(?:" + focusstr + ")"

    matchobjs = []
    matchobj1 =re.findall("(" + Numre + u"{1,10}(?:.{1,3})" + Numre +  u"{1,10}.*?" + focuswords + ")",query)
    matchobj2 =re.findall("(" + focuswords + u"(?:.{,3})" + Numre + u"{1,10}(?:.{1,3})" + Numre + u"{1,10}" + ")",query)
    matchobj3 =re.findall("(" + Scope + "{0,1}" + u"(?:(?:" + Numre + u"{1,10}.*?" + focuswords + ")|(?:" + focuswords + ".*?" + Numre + "{1,10}))" + ".{0,3}"+ Scope + "{0,1}" + Numre + "{0,10}" + ")",query)
    matchobj4 =re.findall(u"(" + focuswords + ")",query)
    
    matchobjs.append(matchobj4)
    matchobjs.append(matchobj3)
    matchobjs.append(matchobj2)
    matchobjs.append(matchobj1)


    result = {}
    matchobjs = [t[-1] for t in matchobjs if t]
    matchobjs = sorted(matchobjs, key=lambda x:len(x))
    for matchobj in matchobjs:
        if matchobj:
            matchres = matchobj.strip().encode("utf-8")
            number = Nf.numberfind(matchres)
            result = Slotxboperate(number,5, matchres, focuswords, 3, 5)
    if result:
        return {"reputation":result}
    return None

def Slotratingfind(queryobj):
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj

    query = query.strip()
    focusstr = u"评价|评级|评分|评星"
    focuswordlist = focusstr.split("|") 
    focuswords = u"(?:" + focusstr + ")" 

    matchobjs = []
    matchobj1 =re.findall("(" + Numre + u"{1,10}(?:.{1,3})" + Numre +  u"{1,10}.*?" + focuswords + ")",query)
    matchobj2 =re.findall("(" + focuswords + u"(?:.{,3})" + Numre + u"{1,10}(?:.{1,3})" + Numre + u"{1,10}" + ")",query)
    matchobj3 =re.findall("(" + Scope + "{0,1}" + u"(?:(?:" + Numre + u"{1,10}.*?" + focuswords + ")|(?:" + focuswords + ".*?" + Numre + "{1,10}))" + ".{0,3}"+ Scope + "{0,1}" + Numre + "{0,10}" + ")",query)
    matchobj4 =re.findall(u"(" + focuswords + ")",query)
    
    matchobjs.append(matchobj4)
    matchobjs.append(matchobj3)
    matchobjs.append(matchobj2)
    matchobjs.append(matchobj1)


    result = {}
    matchobjs = [t[-1] for t in matchobjs if t]
    matchobjs = sorted(matchobjs, key=lambda x:len(x))
    for matchobj in matchobjs:
        if matchobj:
            matchres = matchobj.strip().encode("utf-8")
            number = Nf.numberfind(matchres)
            result = Slotxboperate(number,5, matchres, focuswords, 3,5)
    if result:
        return {"rating":result}
    return None

def Slotxboperate(number = [], maxnumber=1000, matchres = "", default_list = [], default_low = 0, default_high = 9):
    matchres = matchres.decode("utf-8")
    if len(number) == 0:
        for scope in default_list:
            if matchres.find(scope) !=-1:
                return {"lowest":default_low,"highest":default_high}
    elif len(number) !=0:
        number = [float(t) for t in number]
        numall = []
        for num in number:
            if int(num) >10:
                num = num / 10.0
                if num > 10:
                    num = num/10.0
                numall.append(num)
            else:
                numall.append(num)
        for scope in [u"小于", u"以下",u"之内",u"以内",u"不到"]:
            if matchres.find(scope) !=-1:
                return {"lowest":1,"highest":numall[-1]}
        for scope in [u"左右",u"上下"]:
            if matchres.find(scope) !=-1:
                return {"excepted":numall[-1]}
        for scope in [u"以上",u"之上",u"以外", u"大于"]:        
            if matchres.find(scope) !=-1:
                return {"lowest":numall[-1], "highest":maxnumber}

        if len(number) ==2:
            for scope in [u"到", u"至"]:
                if scope in matchres:
                    return {"lowest":numall[-2],"highest":numall[-1]}

        return {"excepted":numall[-1]}

    else:
        return None


if __name__=="__main__":
    #print discount(u"三折到五折的商品")
    for line in sys.stdin:
        print Slotdiscountfind(line.strip().decode("utf-8"))

