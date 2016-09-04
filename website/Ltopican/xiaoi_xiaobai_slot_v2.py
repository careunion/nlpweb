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
import time



reload(sys)
sys.setdefaultencoding("utf-8")

Numre = u"(?:一|二|三|四|五|六|七|八|九|十|\d)"
Numre_str = u"一|二|三|四|五|六|七|八|九|十|\d"
Scope_re = "之外|之上|最低|最高|左右|上下|以下|小于|大于|之内|以上|以内|不到|以外|不大于|不小于|高于|不高于|低于|不低于"
Scope = u"(?:" + Scope_re + ")"
measure_word = "个|台|支|款|米"
Already_dis = 0

Nf = NumberFind()


def Slotdiscountfind(queryobj):

    focusstr = u"折扣|折"
    result = Slotxbreoperate(queryobj,focusstr,0,9.99)
    Already_dis = 0
    if not result:
        return None
    else:
        return {"discount":result}

def Slotreputationfind(queryobj):

    focusstr = u"信用|信用度|诚信"
    result = Slotxbreoperate(queryobj,focusstr,0,5.0)
    Already_dis = 0
    if not result:
        return None
    else:
        return {"reputation":result}

def Slotratingfind(queryobj):

    focusstr = u"星|评价|评级|评星|评论|评分|满意度|满意程度"
    result = Slotxbreoperate(queryobj,focusstr,0,5.0)
    if not result:
        return None
    else:
        return {"rating":result}

def Slotxbreoperate(queryobj,focusstr = "", min = 0, max = 9.0):
    global Already_dis
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj

    query = query.strip()
    focuswordlist = focusstr.split("|") 
    focuswords = u"(?:" + focusstr + ")" 

    matchobjs = []
    matchobj1 =re.findall("(" + Numre + u"{1,10}(?:.{0,3}?)(?:到|至)" + Numre +  u"{1,10}.{0,3}?" + focuswords + ")",query)
    matchobj2 =re.findall("(" + focuswords + u"(?:.{,3})" + Numre + u"{1,10}(?:.{0,3}?)(?:到|至)" + Numre + u"{1,10}" + ")",query)
    #matchobj4 =re.findall("(" + focuswords + u"(?:.{0,3}?)" + Numre + "{1,10}" + u"[^个台支款米]{0,2}?" + Scope + "{0,1}" + ")",query)
    matchobj4 =re.findall("(" + focuswords + u"(?!不错){0,3}?" + Numre + "{1,10}" + u"[^个台支款米]{0,2}?" + Scope + "{0,1}" + ")",query)
    #matchobj3 =re.findall("(" + Scope + "{0,1}" +  Numre + "{1,10}" + "(?:.{0,2})?"  + u"(?!" + measure_word + ")" + focuswords + Numre + "{0,10}" + Scope + "{0,1})",query)
    matchobj3 =re.findall("(" + Scope + "{0,1}" +  Numre + "{1,10}" + u"[^个台支款米]{0,2}?"  + focuswords + Numre + "{0,10}" + Scope + "{0,1})",query)
    matchobj5 =re.findall(u"([^一二三四五六七八九十\d]{1,3}" + focuswords + ")",query)
    if matchobj5:
        if re.search(Numre,matchobj5[-1]):
            matchobj5[-1] = []
            
    matchobj6 =re.findall(u"(" + focuswords + u"[^一二三四五六七八九十\d]{1,3})",query)
    if matchobj6:
        if re.search(Numre,matchobj6[-1]):
            matchobj6[-1] = []
    
    matchobjs.append(matchobj5)
    matchobjs.append(matchobj6)
    matchobjs.append(matchobj4)
    matchobjs.append(matchobj3)
    matchobjs.append(matchobj2)
    matchobjs.append(matchobj1)
    #print matchobjs

    result = {}
    matchobjs = [t[-1] for t in matchobjs if t]
    #matchobjs = sorted(matchobjs, key=lambda x:len(x))
    #if matchobj6:
    #    matchobjs.insert(0,matchobj6[-1])
    #    if matchobj5:
    #        matchobjs.insert(1,matchobj5[-1])
    #else:
    #    if matchobj5:
    #        matchobjs.insert(0,matchobj5[-1])
    #print matchobjs
    last_result = []
    last_tag = []
    for matchobj in matchobjs:
        if matchobj:
            matchres = matchobj.strip().encode("utf-8")
            #print matchres,"-------------"
            number = Nf.numberfind(matchres)
            result,tag = Slotxbnumoperate(number, max , matchres, focuswords, min, max)
            #print tag

            if tag:
                last_result.append(result)
                last_tag.append(tag)
                #print last_result
                #print last_tag

            if last_tag:
                if len(last_tag)>1:
                    if last_tag[-1] == "2" and last_tag[-2] == "1":
                        result = last_result[-2]
    #print last_result            
    return result

def containAny(seq,aset):
    for c in seq:
        if c in aset:
            return True
    return False


def Slotxbnumoperate(number = [], maxnumber=1000, matchres = "", default_list = [], default_low = 0, default_high = 9.0):
    #global Already_dis
    matchres = matchres.decode("utf-8")

    asses_high = {"好","优","很好","非常好","高","不错","信用","诚信"}
    asses_low = {"低","不好","差","失信","一般"}

    if len(number) == 0:
        for scope in default_list:
            if matchres.find(scope) !=-1:
                if containAny(asses_low,matchres):
                    #print "1"
                    #Already_dis = 1
                    return {"lowest":default_low,"highest":default_high * 0.6},"1"
                elif containAny(asses_high,matchres):
                    Already_dis = 1
                    #print "2",Already_dis
                    #print default_high
                    #print "ok"
                    #return "ok"
                    return {"lowest":default_high * 0.6,"highest":default_high},"1"   
                else:
                    #if Already_dis == 0:
                    #    print "3"
                    return {"lowest":default_low,"highest":default_high},"2"

    elif len(number) !=0:
        number = [float(t) for t in number]
        #print number
        numall = []
        for num in number:
            if int(num) >10:
                num = num / 10.0
                if num > 10:
                    num = num/10.0
                numall.append(num)
            else:
                numall.append(num)
        #print numall
        numall = [num if num <= maxnumber else maxnumber for num in numall]
        #print numall
        if len(numall) > 1:
            for scope in [u"到", u"至"]:
                if scope in matchres :
                    return {"lowest":numall[-2],"highest":numall[-1]},None

        for scope in [u"最高",u"小于", u"以下",u"之内",u"以内",u"不到",u"不大于",u"低于",u"不高于"]:
            if matchres.find(scope) !=-1 and not re.search(u"不低于|不小于",matchres):
                return {"lowest":0,"highest":numall[-1]},None
        for scope in [u"左右",u"上下"]:
            if matchres.find(scope) !=-1:
                return {"excepted":numall[-1]},None
        for scope in [u"之上",u"之外",u"最低",u"以上",u"之上","以外",u"大于",u"不小于",u"高于",u"不低于"]:        
            if matchres.find(scope) !=-1:
                return {"lowest":numall[-1], "highest":maxnumber},None

        return {"excepted":numall[-1]},None

    else:
        return None,None


if __name__=="__main__":
    #t = time.time()
    ##print discount(u"三折到五折的商品")(line.strip().decode("utf-8")
    #for line in sys.stdin:
    ##if Slotdiscountfind(line.strip().decode("utf-8")):
    #    print line.strip().decode("utf-8"),"\t",Slotdiscountfind(line.strip().decode("utf-8"))
    ##elif Slotreputationfind(line.strip().decode("utf-8")):
    #    print line.strip().decode("utf-8"),"\t",Slotreputationfind(line.strip().decode("utf-8"))
    ##elif Slotratingfind(line.strip().decode("utf-8")):
    #    print line.strip().decode("utf-8"),"\t",Slotratingfind(line.strip().decode("utf-8"))
    #    print ""
    #print "time:",time.time()-t
    for line in sys.stdin:

        line = line.strip().decode('utf-8')
        discount = Slotdiscountfind(line)
        if not discount:
           discount = None
        reputation = Slotreputationfind(line)
        if not reputation:
           reputation = None
        rating = Slotratingfind(line)
        if not rating:
           rating = None
        #print line,'\t距离:',Slotdistancefind(line),'\t关注度',Slotattentionfind(line),'\t价格',Slotpricefind(line)
        print '\t折扣',discount,'\t信用',reputation,'\t评价',rating
        print ""
