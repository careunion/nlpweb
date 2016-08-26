#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: Slots.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-22 14:17:29
#########################################################################
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import re
import json

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
#转换工具模块

common_used_numerals = {'〇':0, 'O':0, '零':0, \
        '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, \
        '百':100, '千':1000, '万':10000, '亿':100000000, \
        '两':2, '壹':1, '贰':2, '叁':3, '肆':4, '伍':5, '陆':6, '柒':7, '扒':8, '玖':9, '拾':10, '佰':100, '仟':1000, \
        '仟万':10000000, '千万':10000000, '百万':1000000, '佰万':1000000, '十万':100000, '拾万':100000 \
        }   

def numbertrans(numcn):
        split_cns = ["亿", "千万", "仟万", "百万", "佰万", "十万", "拾万", "万", "千", "仟", "佰", "百", "十", "拾"]
    
        if numcn.isdigit():
            #如果是数字，直接转为数字
            return int(numcn)
    
        #从最大的单位开始分割，然后 upper * 最大单位 + lower, 然后 upper 跟 lower 各自递归撒
        #如         二亿零四十万  ==   二 * 亿       + 零四十万
        for cn_num in split_cns:
            nums = numcn.split(cn_num)
            if len(nums) > 1:
                upper = numbertrans(nums[0])
                lower = numbertrans(nums[1])
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


#校验范围(3到5百)
def checkRange(num1,num2):

    if num1 <= 0 or num1 >= 9:
        return num1,num2

    num2str = str(num2)
    zeronum = num2str.count('0')
    nonzeronum = len(num2str) - zeronum
    if (nonzeronum != 1) or (zeronum == 0):
        return num1,num2
    firstnum = int(num2str[0])
    if num1 > firstnum:
        return num1,num2

    return num1*(10**zeronum),num2
    

def Slotdistancefind(queryobj):
    """
        获取距离参数。
    """
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj

    numstr = u"(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
    numextend = numstr + u"+(?:(?:\.|点)" + numstr + "+){0,1}"
    vaguestr = u'(附近|旁边|周围|这里)'
    unitstr = u'(公里|里|千米|k米|米)'
    timestr = u'(分钟|小时|分)'
    modestr = u'(步行|走路|开车|坐车|打车|乘车|打的)'
    type1str = u'(小于|不到|少于|短于|只要)?'
    type2str = u'(以内|之内|以下|左右)?'
    markstr = u'(?:距离|路程|远近)'
    
    res = {}
    #locate
    locatere = re.compile(u'万象城|南山海岸城|购物公园')
    _obj = locatere.search(query)
    if _obj:
        locate = _obj.group()
    else:
        locate = ''
    infoDict = {}
    if locate:
        infoDict['locate'] = locate
    #distance
    distance = ''
    position = -1
    pattern0 = re.compile(u'(' + vaguestr + '?.{0,3}(' + numextend + u')' + unitstr +'?(?:到|至)' + '(' + numextend + ')' + unitstr + u')')
    _obj = re.findall(pattern0, query)
    if _obj:
        _obj = [_obj[-1]]
        for distance_cn in _obj:
            newPosition = query.rfind(distance_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            flag1 = False
            flag2 = False
            vague_cn = distance_cn[1] 
            num1_cn = distance_cn[2]
            unit1_cn = distance_cn[3]
            num2_cn = distance_cn[4]
            unit2_cn = distance_cn[5]
            if unit2_cn == u'公里' or unit2_cn == u'k米':
                num2_base = 1000.0
            elif unit2_cn == u'里':
                num2_base = 500.0
            else:
                num2_base = 1.0
            num2_cns = re.split(u"(?:点|\.)", num2_cn)
            num2 = -1
            if len(num2_cns) == 1:
                if num2_cns[0][-1] == u'千' and num2_cns[0][:-1].isdigit():
                    num2_base = 1000.0
                    num2_cns[0] = num2_cns[0][:-1] 
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                num2 = int(pre_num)
                flag2 = True
            elif len(num2_cns) == 2:
                if unit2_cn == u'米' and (num2_cns[1][-1] == '千'):
                    num2_base = 1000.0
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num2_cns[1].encode('utf-8'))))
                num2 = pre_num + aft_num
            num1_cns = re.split(u"(?:点|\.)", num1_cn)
            num1 = -1
            if len(num1_cns) == 1:
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                num1 = int(pre_num)
                flag1 = True
            elif len(num1_cns) == 2:
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num1_cns[1].encode('utf-8'))))
                num1 = pre_num + aft_num
            if flag1 and flag2 and (not unit1_cn):
                num1,num2 = checkRange(num1,num2)
            if unit1_cn:
                if unit1_cn == u'公里' or unit1_cn == u'k米' or unit1_cn == u'千米':
                    num1_base = 1000.0
                elif unit1_cn == u'里':
                    num1_base = 500.0
                else:
                    num1_base = 1.0
            else:
                num1_base = num2_base
            if num1 >0 and num2 >0:
                num1 = num1*num1_base
                num2 = num2*num2_base               
                distance = str(num1) + u'米,' + str(num2) + u'米' 
            if vague_cn:
                query = query.replace(vague_cn,'')
    pattern1 = re.compile(u'(' + vaguestr + '?' + type1str + '.{0,3}?(' + numextend + ')' + unitstr + type2str + u')')
    _obj = re.findall(pattern1, query)
    if _obj:
        _obj = [_obj[-1]]
        for distance_cn in _obj:
            newPosition = query.rfind(distance_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            vague_cn = distance_cn[1]
            type_cn = ''
            if distance_cn[2]:
                type_cn = distance_cn[2]
            elif distance_cn[5]:
                type_cn = distance_cn[5]
            num_cn = distance_cn[3]
            unit_cn = distance_cn[4]
            if unit_cn == u'公里':
                num_base = 1000.0
            elif unit_cn == u'里':
                num_base = 500.0
            else:
                num_base = 1.0
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                distance = str(pre_num) + u'米'
            elif len(num_cns) == 2:
                if unit_cn == u'米' and (num_cns[1][-1] == '千' or num_cns[1][-1] == 'k'):
                    num_base = 1000.0
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8')))) * num_base
                distance = str(pre_num + aft_num) + u'米'
            if vague_cn:
                query = query.replace(vague_cn,'')
            if type_cn == u'以内' or type_cn == u'之内' or type_cn == u'以下' or distance_cn[2]:
                distance = u'0米,' + distance
    pattern2 = re.compile(u'(' + vaguestr + '?' + modestr + type1str + '.{0,3}?(' + numextend + ')' + timestr + type2str + u')')
    _obj = re.findall(pattern2, query)
    if _obj:
        _obj = [_obj[-1]]
        for distance_cn in _obj:
            newPosition = query.rfind(distance_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            vague_cn = distance_cn[1] 
            unit_cn = distance_cn[2]
            type_cn = ''
            if distance_cn[3]:
                type_cn = distance_cn[3]
            elif distance_cn[6]:
                type_cn = distance_cn[6]
            num_cn = distance_cn[4]
            time_cn = distance_cn[5]
            if unit_cn == u'步行' or unit_cn == u'走路':
                num_base = 30.0
            elif unit_cn == u'开车' or unit_cn == u'坐车'or unit_cn == u'打车' or unit_cn == u'乘车' or unit_cn == u'打的':
                num_base = 500.0
            else:
                num_base = 30.0
            if time_cn == u'小时':
                num_base = num_base * 60
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                distance = str(pre_num) + u'米'
            elif len(num_cns) == 2:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8')))) * num_base
                distance = str(pre_num + aft_num) + u'米'
            if vague_cn:
                query = query.replace(vague_cn,'')
            #if type_cn == u'以内' or type_cn == u'之内' or type_cn == u'以下' or distance_cn[3]:
            distance = u'0米,' + distance
    pattern3 = re.compile(u'(' + vaguestr + '?' + type1str + '.{0,3}?(' + numextend + ')' + timestr + modestr + type2str + u')')
    _obj = re.findall(pattern3, query)
    if _obj:
        _obj = [_obj[-1]]
        for distance_cn in _obj:
            newPosition = query.rfind(distance_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            vague_cn = distance_cn[1]
            type_cn = ''
            if distance_cn[2]:
                type_cn = distance_cn[2]
            elif distance_cn[6]:
                type_cn = distance_cn[6]
            num_cn = distance_cn[3]
            time_cn = distance_cn[4]
            unit_cn = distance_cn[5]
            if unit_cn == u'步行' or unit_cn == u'走路':
                num_base = 30.0
            elif unit_cn == u'开车' or unit_cn == u'坐车'or unit_cn == u'打车' or unit_cn == u'乘车' or unit_cn == u'打的':
                num_base = 500.0
            else:
                num_base = 30.0
            if time_cn == u'小时':
                num_base = num_base * 60
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                distance = str(pre_num) + u'米'
            elif len(num_cns) == 2:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8')))) * num_base
                distance = str(pre_num + aft_num) + u'米'
            if vague_cn:
                query = query.replace(vague_cn,'')
            #if type_cn == u'以内' or type_cn == u'之内' or type_cn == u'以下' or distance_cn[2]:
            distance = u'0米,' + distance
    pattern4 = re.compile(u'(' + vaguestr + '?' + markstr + type1str + '.{0,3}?(' + numextend + ')' + '[^公里|里|千米|k米|米]*' + type2str + u')')
    _obj = re.findall(pattern4, query)
    if _obj:
        _obj = [_obj[-1]]
        for distance_cn in _obj:
            #print distance_cn
            newPosition = query.rfind(distance_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            vague_cn = distance_cn[1]
            type_cn = ''
            if distance_cn[2]:
                type_cn = distance_cn[2]
            elif distance_cn[4]:
                type_cn = distance_cn[4]
            num_cn = distance_cn[3]
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8'))
                distance = str(float(pre_num)) + u'米'
            elif len(num_cns) == 2:
                pre_num = numbertrans(num_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8'))))
                distance = str(pre_num + aft_num) + u'米'
            if vague_cn:
                query = query.replace(vague_cn,'')
            if type_cn == u'以内' or type_cn == u'之内' or type_cn == u'以下' or distance_cn[1]:
                distance = u'0米,' + distance
    pattern5 = re.compile(u'(附近|周围|旁边)')
    _obj = re.findall(pattern5, query)
    if _obj:
        _obj = [_obj[-1]]
        for distance_cn in _obj:
            newPosition = query.rfind(distance_cn[0])
            if newPosition <= position:
                break
            else:
                distance = u'0米,500米'
    
    if distance:
        resList = distance.split(',')
        if len(resList) == 1:
            infoDict['excepted'] = float(resList[0][:-1])
        elif len(resList) == 2:
            infoDict['lowest'] = float(resList[0][:-1])
            infoDict['highest'] = float(resList[1][:-1])
        res['distance'] = infoDict
    if infoDict:
        return res
        #return json.dumps(res,ensure_ascii = False)
    else:
        return None


def pricequeryextend(query):
    discount = u"折|折扣"
    price = u"价格|价钱|金额|价位|价码|元|块钱|块"
    distance = u"公里|里|千米|k米|米|分钟|小时|分|步行|走路|开车|坐车|打车|乘车|打的|距离|路程|远近"
    attention = u"关注度|热度"
    rating = u"评价|星"
    reputation = u"信用|诚信"
    others = u"其他"

    numre = u"((?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿){2,5})"

    words = [discount, price, distance, attention, rating, reputation, others]

    _re = "(" + "|".join(words) + ")" 
    
    matchobj = re.search(_re, query)
    if matchobj:
        return query

    return re.sub(numre, ur"\1块钱", query)


def Slotpricefind(queryobj, maxPrice = 1000000):
    """
        获取价格参数。
    """
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj
    query = pricequeryextend(query)

    numstr = u"(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
    numextend = numstr + u"+(?:(?:\.|点)" + numstr + "+){0,1}"
    type1str = u'(小于|不到|少于|只要|低于|不足|大于|高于|多于|不低于|不少于|不小于)?'
    type2str = u'(以内|之内|以下|以上|之上|左右|上下)?'
    unitstr = u'(?:元钱|块钱|元|块)'
    perstr = u'(' + numstr + u')' + u'(?:个人|人)'
    markstr = u'(?:价格|价钱|单价|消费|每人|人均|价位|价码|金额)'
    
    res = {}
    infoDict = {}
    #price
    price = ''
    position = -1
    pattern0 = re.compile(u'(' + u'(' + numextend + u')' + unitstr +'(?:到|至)' + u'(' + numextend + u')' + unitstr + u')')
    _obj = re.findall(pattern0, query)
    if _obj:
        _obj = [_obj[-1]]
        for price_cn in _obj:
            newPosition = query.rfind(price_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            flag1 = False
            flag2 = False
            num1_cn = price_cn[1]
            num2_cn = price_cn[2]
            num2_base = 1.0
            num2_cns = re.split(u"(?:点|\.)", num2_cn)
            num2 = -1
            if len(num2_cns) == 1:
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                num2 = int(pre_num)
                flag2 = True
            elif len(num2_cns) == 2:
                if num2_cns[1][-1] == u'万':
                    num2_base = 10000.0
                    num2_cns[1] = num2_cns[1][:-1]
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num2_cns[1].encode('utf-8'))))
                num2 = pre_num + aft_num
            num1_base = 1.0
            num1_cns = re.split(u"(?:点|\.)", num1_cn)
            num1 = -1
            if num2_base == 10000.0:
                num1_base = num2_base
            if len(num1_cns) == 1:
                if num1_cns[0][-1] == u'万':
                    num1_cns[0] = num1_cns[0][:-1]
                if not num1_cns[0].isdigit():
                    num1_base = 1.0
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                num1 = int(pre_num)
                flag1 = True
            elif len(num1_cns) == 2:
                if num1_cns[1][-1] == u'万':
                    num1_cns[1] = num1_cns[1][:-1]
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num1_cns[1].encode('utf-8'))))
                num1 = pre_num + aft_num
            if flag1 and flag2:
                num1,num2 = checkRange(num1,num2)
            if num1 >0 and num2 >0:
                num1 = num1*num1_base
                num2 = num2*num2_base               
                price = str(num1) + u'元,' + str(num2) + u'元' 
    pattern1 = re.compile(u'(' + perstr + type1str + u'.{0,3}?(' + numextend + u')'+ unitstr + '?' + type2str + u')')
    _obj = re.findall(pattern1, query)
    if _obj:
        _obj = [_obj[-1]]
        for price_cn in _obj:
            newPosition = query.rfind(price_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            type_cn = ''
            per_cns = price_cn[1]
            if price_cn[2]:
                type_cn = price_cn[2]
            elif price_cn[4]:
                type_cn = price_cn[4]
            num_cn = price_cn[3]
            num_base = 1.0
            per_num = numbertrans(per_cns.encode('utf-8'))
            print per_num
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                print pre_num
                price = str(pre_num/per_num) + u'元'
            elif len(num_cns) == 2:
                if num_cns[1][-1] == '万':
                    num_base = 10000.0
                    num_cns[1] = num_cns[1][:-1]
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8')))) * num_base
                price = str((pre_num + aft_num)/per_num) + u'元'
            if type_cn in [u'小于',u'不到',u'少于',u'只要',u'低于',u'不足',u'以内',u'之内',u'以下']:
                price = u'0元,' + price
                print price
            elif type_cn in [u'大于',u'高于',u'多于',u'不低于',u'不少于',u'不小于',u'以上',u'之上']:
                 price = price + ',' + str(maxPrice) + u'元'
            elif type_cn in [u'左右',u'上下']:
                pass
            else:
                pass
    pattern2 = re.compile(u'(' + type1str + '.{0,3}?(' + numextend + ')' + unitstr + type2str + u')')
    _obj = re.findall(pattern2, query)
    if _obj:
        _obj = [_obj[-1]]
        for price_cn in _obj:
            newPosition = query.rfind(price_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            type_cn = ''
            if price_cn[1]:
                type_cn = price_cn[1]
            elif price_cn[3]:
                type_cn = price_cn[3]
            num_cn = price_cn[2]
            num_base = 1.0
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                price = str(pre_num) + u'元'
            elif len(num_cns) == 2:
                if num_cns[1][-1] == '万':
                    num_base = 10000.0
                    num_cns[1] = num_cns[1][:-1]
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8')))) * num_base
                price = str(pre_num + aft_num) + u'元'
            if type_cn in [u'小于',u'不到',u'少于',u'只要',u'低于',u'不足',u'以内',u'之内',u'以下']:
                price = u'0元,' + price
            elif type_cn in [u'大于',u'高于',u'多于',u'不低于',u'不少于',u'不小于',u'以上',u'之上']:
                 price = price + ',' + str(maxPrice) + u'元'
            elif type_cn in [u'左右',u'上下']:
                pass
            else:
                pass
    pattern3 = re.compile(u'(' + markstr + type1str + '.{0,3}?(' + numextend + ')' + unitstr + '?' + type2str + u')')
    _obj = re.findall(pattern3, query)
    if _obj:
        _obj = [_obj[-1]]
        for price_cn in _obj:
            newPosition = query.rfind(price_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            type_cn = ''
            if price_cn[1]:
                type_cn = price_cn[1]
            elif price_cn[3]:
                type_cn = price_cn[3]
            num_cn = price_cn[2]
            num_base = 1.0
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                price = str(pre_num) + u'元'
            elif len(num_cns) == 2:
                if num_cns[1][-1] == '万':
                    num_base = 10000.0
                    num_cns[1] = num_cns[1][:-1]
                pre_num = numbertrans(num_cns[0].encode('utf-8')) * num_base
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8')))) * num_base
                price = str(pre_num + aft_num) + u'元'
            if type_cn in [u'小于',u'不到',u'少于',u'只要',u'低于',u'不足',u'以内',u'之内',u'以下']:
                price = u'0元,' + price
            elif type_cn in [u'大于',u'高于',u'多于',u'不低于',u'不少于',u'不小于',u'以上',u'之上']:
                 price = price + ',' + str(maxPrice) + u'元'
            elif type_cn in [u'左右',u'上下']:
                pass
            else:
                pass
    if price:
        resList = price.split(',')
        if len(resList) == 1:
            infoDict['excepted'] = float(resList[0][:-1])
        elif len(resList) == 2:
            infoDict['lowest'] = float(resList[0][:-1])
            infoDict['highest'] = float(resList[1][:-1])
        res['price'] = infoDict
        return res
        #return json.dumps(res,ensure_ascii = False)
    else:
        return None


def Slotattentionfind(queryobj, maxAttention = 1000):
    """
        获取价格参数。
    """
    if type(queryobj) is not unicode:
        query = queryobj.rawtext
    else:
        query = queryobj

    numstr = u"(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
    numextend = numstr + u"+(?:(?:\.|点)" + numstr + "+){0,1}"
    type1str = u'(小于|不到|少于|只要|低于|不足|大于|高于|多于|不低于|不少于|不小于)?'
    type2str = u'(以内|之内|以下|以上|之上|左右|上下)?'
    headmarkstr = u'(?:关注|关注度|关注量|访问量|购买量|人流量|点击量)'
    tailmarkstr = u'(?:关注度|关注量|访问量|购买量|人流量|点击量)'
    
    res = {}
    infoDict = {}
    #attention
    attention = ''
    position = -1
    pattern0 = re.compile(u'(' + headmarkstr + u'.{0,3}?(' + numextend + u')' +'(?:到|至)' + u'(' + numextend + u')' + u')')
    _obj = re.findall(pattern0, query)
    if _obj:
        _obj = [_obj[-1]]
        for attention_cn in _obj:
            newPosition = query.rfind(attention_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            flag1 = False
            flag2 = False
            num1_cn = attention_cn[1]
            num2_cn = attention_cn[2]
            num2_cns = re.split(u"(?:点|\.)", num2_cn)
            num2 = -1
            if len(num2_cns) == 1:
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                num2 = int(pre_num)
                flag2 = True
            elif len(num2_cns) == 2:
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num2_cns[1].encode('utf-8'))))
                num2 = pre_num + aft_num
            num1_cns = re.split(u"(?:点|\.)", num1_cn)
            num1 = -1
            if len(num1_cns) == 1:
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                num1 = int(pre_num)
                flag1 = True
            elif len(num1_cns) == 2:
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num1_cns[1].encode('utf-8'))))
                num1 = pre_num + aft_num
            if flag1 and flag2:
                num1,num2 = checkRange(num1,num2)
            if num1 >0 and num2 >0:
                attention = str(num1) + u'点,' + str(num2) + u'点' 
    pattern1 = re.compile(u'(' + u'(' + numextend + u')' +'(?:到|至)' + u'(' + numextend + u')' + tailmarkstr + u')')
    _obj = re.findall(pattern1, query)
    if _obj:
        _obj = [_obj[-1]]
        for attention_cn in _obj:
            newPosition = query.rfind(attention_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            flag1 = False
            flag2 = False
            num1_cn = attention_cn[1]
            num2_cn = attention_cn[2]
            num2_cns = re.split(u"(?:点|\.)", num2_cn)
            num2 = -1
            if len(num2_cns) == 1:
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                num2 = int(pre_num)
                flag2 = True
            elif len(num2_cns) == 2:
                pre_num = numbertrans(num2_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num2_cns[1].encode('utf-8'))))
                num2 = pre_num + aft_num
            num1_cns = re.split(u"(?:点|\.)", num1_cn)
            num1 = -1
            if len(num1_cns) == 1:
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                num1 = int(pre_num)
                flag1 = True
            elif len(num1_cns) == 2:
                pre_num = numbertrans(num1_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num1_cns[1].encode('utf-8'))))
                num1 = pre_num + aft_num
            if flag1 and flag2:
                num1,num2 = checkRange(num1,num2)
            if num1 >0 and num2 >0:
                attention = str(num1) + u'点,' + str(num2) + u'点' 
    pattern2 = re.compile(u'(' + headmarkstr + type1str + '.{0,3}?(' + numextend + ')' + type2str + u')')
    _obj = re.findall(pattern2, query)
    if _obj:
        _obj = [_obj[-1]]
        for attention_cn in _obj:
            newPosition = query.rfind(attention_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            type_cn = ''
            if attention_cn[1]:
                type_cn = attention_cn[1]
            elif attention_cn[3]:
                type_cn = attention_cn[3]
            num_cn = attention_cn[2]
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8'))
                attention = str(pre_num) + u'元'
            elif len(num_cns) == 2:
                pre_num = numbertrans(num_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8'))))
                attention = str(pre_num + aft_num) + u'元'
            if type_cn in [u'小于',u'不到',u'少于',u'只要',u'低于',u'不足',u'以内',u'之内',u'以下']:
                attention = u'0元,' + price
            elif type_cn in [u'大于',u'高于',u'多于',u'不低于',u'不少于',u'不小于',u'以上',u'之上']:
                 attention = price + ',' + str(maxPrice) + u'元'
            elif type_cn in [u'左右',u'上下']:
                pass
            else:
                pass
    pattern3 = re.compile(u'(' + type1str + '.{0,3}?(' + numextend + ')' + tailmarkstr + type2str + u')')
    _obj = re.findall(pattern3, query)
    if _obj:
        _obj = [_obj[-1]]
        for attention_cn in _obj:
            newPosition = query.rfind(attention_cn[0])
            if newPosition <= position:
                break
            else:
                position = newPosition
            type_cn = ''
            if attention_cn[1]:
                type_cn = attention_cn[1]
            elif attention_cn[3]:
                type_cn = attention_cn[3]
            num_cn = attention_cn[2]
            num_cns = re.split(u"(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = numbertrans(num_cns[0].encode('utf-8'))
                attention = str(pre_num) + u'元'
            elif len(num_cns) == 2:
                pre_num = numbertrans(num_cns[0].encode('utf-8'))
                aft_num = float('0.' + str(numbertrans(num_cns[1].encode('utf-8'))))
                attention = str(pre_num + aft_num) + u'元'
            if type_cn in [u'小于',u'不到',u'少于',u'只要',u'低于',u'不足',u'以内',u'之内',u'以下']:
                attention = u'0元,' + price
            elif type_cn in [u'大于',u'高于',u'多于',u'不低于',u'不少于',u'不小于',u'以上',u'之上']:
                 attention = price + ',' + str(maxPrice) + u'元'
            elif type_cn in [u'左右',u'上下']:
                pass
            else:
                pass
    if attention:
        resList = attention.split(',')
        if len(resList) == 1:
            #print resList[0][:-1]
            infoDict['excepted'] = float(resList[0][:-1])
        elif len(resList) == 2:
            infoDict['lowest'] = float(resList[0][:-1])
            infoDict['highest'] = float(resList[1][:-1])
        res['attention'] = infoDict
        return res
        #return json.dumps(res,ensure_ascii = False)
    else:
        return None

if __name__=="__main__":
    for line in sys.stdin:
        line = line.strip().decode('utf-8')
        print Slotdistancefind(line)
        print Slotattentionfind(line)
        print Slotpricefind(line)
        #print numbertrans(line)
