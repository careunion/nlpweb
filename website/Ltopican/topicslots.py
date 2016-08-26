#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topicslots.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-09 13:09:53
#########################################################################
import re
import os
import esTopic
import json

from slotfuc_weather import *
from slotfuc_weathercity import *
from slotfuc_xiaoi import *

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
essearchobj = esTopic.esTopic()

###########----------------slot1 ---numbers
common_used_numerals = {'〇':0, 'O':0, '零':0, \
        '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, \
        '百':100, '千':1000, '万':10000, '亿':100000000, \
        '两':2, '壹':1, '贰':2, '叁':3, '肆':4, '伍':5, '陆':6, '柒':7, '扒':8, '玖':9, '拾':10, '佰':100, '仟':1000, \
        '仟万':10000000, '千万':10000000, '百万':1000000, '佰万':1000000, '十万':100000, '拾万':100000 \
        }   
def Slotnumbertrans(numcn):
    split_cns = ["亿", "千万", "仟万", "百万", "佰万", "十万", "拾万", "万", "千", "仟", "佰", "百", "十", "拾"]

    if numcn.isdigit():
        #如果是数字，直接转为数字
        return int(numcn)

    #从最大的单位开始分割，然后 upper * 最大单位 + lower, 然后 upper 跟 lower 各自递归撒
    #如         二亿零四十万  ==   二 * 亿       + 零四十万
    for cn_num in split_cns:
        nums = numcn.split(cn_num)
        if len(nums) > 1:
            upper = Slotnumbertrans(nums[0])
            lower = Slotnumbertrans(nums[1])
            return upper * common_used_numerals[cn_num] + lower
    
    numcn_len = len(numcn)
    if numcn_len == 3:
        #刚好是一个字的时候，取字典内的数字
        return common_used_numerals[numcn]
    elif numcn_len > 3:
        #如果是多个字，[0-9]的汉字，直接转成相应的数字
        numcns = [t.encode("utf-8") for t in numcn.decode("utf-8")]
        nums = ""
        for _num in numcns:
            if _num.isdigit():
                nums += _num
                continue
            nums += str(common_used_numerals[_num])
        return int(nums)
    elif numcn_len == 0:
        return 0

def Slotnumberfind(queryobj):
    cn_str = queryobj.rawtext
    if type(cn_str) is unicode:
        cn_str = cn_str.encode("utf-8")
    numstr = "(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
    numre = re.compile(numstr + "+(?:(?:\.|点)" + numstr + "+){0,1}")
    _obj = re.findall(numre, cn_str)
    if not _obj:
        return None

    num_list = []
    for num_cn in _obj:
        num_cns = re.split("(?:点|\.)", num_cn)
        if len(num_cns) == 1:
            pre_num = Slotnumbertrans(num_cns[0])
            num_list.append( str(pre_num)  )
        elif len(num_cns) == 2:
            pre_num = Slotnumbertrans(num_cns[0])
            aft_num = Slotnumbertrans(num_cns[1])
            num_list.append( str(pre_num) + "." + str(aft_num) )
    if num_list:
        return {"number" : num_list}
    else:
        return None

#########----------------slot2 --- date
Datere = u"(上|下|前|后)?(一|二|三|四)?(个)?(周|礼拜)(一|二|三|四|五|六|七|日|天|.{0,2}(?:今天|明天|昨天|前天|大前天|后天|大后天))"

def Slotdatefind(queryobj):
    query = queryobj.rawtext
    if type(query) is not unicode:
        query = query.decode("utf-8")
    matchobj1 = re.search(u"(今天|明天|昨天|前天|大前天|后天|大后天|(一|二|三|四|五|六|七|八|九|十)(日|天)(前|后)|月.{1,3}(日|号)|(一|二|三|四|五|六|七|八|九|十)号)", query)
    matchobj2 = re.search(Datere, query)

    result = None
    if matchobj1:
        result = matchobj1.group()
    elif matchobj2:
        result = matchobj2.group()
    if result:
        dayrange, dateday = DateTrans(queryobj.rawtext)
        result = str(dateday)

    if result:
        return {"Date": result, "Days_r":dayrange}
    else:
        return None


#########----------------slot2 --- city
weathercityobj = IdentWeatherCity()
def Slotcityfind(queryobj):
    query = queryobj.rawtext
    if type(query) is not unicode:
        query = query.decode("utf-8")
    city = weathercityobj.main(query)
    if not city:
        return None
    else:
        return {"City": city}

######-------slot- SlotplanClassify
def SlotplanClassify(queryobj):
    query = queryobj.rawtext
    #query扩展
    new_query = essearchobj.queryExtend(queryobj)
    #取查询结果
    res_json = essearchobj.multifiledsearch("xiaolan", "sportlist0815v2", 5, new_query, [["content", 2],["title", 1]])
    #重排返回具体字段值
    res_rerank_json = essearchobj.resRerank(res_json, ["Keyid", "title"])

    #过滤<0.2的
    res_rerank_json = [ t for t in res_rerank_json if t.get("Score") >= 0.2]

    if res_rerank_json:
        return {"Topn": res_rerank_json}
    else:
        return None

def Slotbrandsearch(queryobj):
    query = queryobj.rawtext
    new_query_posseg = [word for word,pos in queryobj.postext if pos in ["n", "br", "nr", "nz", "nt"]]
    new_query = " ".join(new_query_posseg)

    print "query extend", query, "->", new_query
    #print json.dumps(queryobj.postext, ensure_ascii=False)
    
    if not new_query:
        return None

    #获取query关键字段
    ns_query_list = [word for word,pos in queryobj.postext if pos in ["n", "nr", "nz", "nt"]]
    br_query_list = [word for word,pos in queryobj.postext if pos in ["br"]]
    ns_query = " ".join(ns_query_list) 
    br_query = " ".join(br_query_list) 

    #取查询结果
    res_json = essearchobj.multifiledsearch("xiaoi", "productinfo20160818", 20, new_query, [["storeName", 1],["productName", 1], ["categoryName", 1.5]])
    #重排返回具体字段值
    res_rerank_json = essearchobj.resRerank(res_json, ["storeName", "productName", "categoryName"])
    #print json.dumps(res_rerank_json, ensure_ascii=False)

    #过滤 与query太不一致的,分值太低的
    rerank_json = []
    for result in res_rerank_json:
        if result.get("Score") < 0.2:continue
        storeName = result.get("storeName", "")
        productName = result.get("productName", "")
        result["item_keyword"] = ns_query
        result["store_keyword"] = br_query
        if len(new_query) <= 3 and len(set(new_query)&set(storeName + productName)) >= 2:
            rerank_json.append(result)
        elif len(new_query) > 3 and len(set(new_query)&set(storeName + productName)) >= 2:#len(set(new_query)) /4:
            rerank_json.append(result)
        #print storeName, productName, result["categoryName"], result["Score"]
        #print len(set(new_query)&set(storeName + productName)), len(set(new_query))

    if rerank_json:
        return {"Topn": rerank_json}
    else:
        return None
