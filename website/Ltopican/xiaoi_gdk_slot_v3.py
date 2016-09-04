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
import time

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
#数字查找、转换类
class SlotNumberFind(object):
    def __init__(self):
        self.common_used_numerals = {'〇':0, 'O':0, '零':0, \
        '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, \
        '百':100, '千':1000, '万':10000, '亿':100000000, \
        '两':2, '壹':1, '贰':2, '叁':3, '肆':4, '伍':5, '陆':6, '柒':7, '扒':8, '玖':9, '拾':10, '佰':100, '仟':1000, \
        '仟万':10000000, '千万':10000000, '百万':1000000, '佰万':1000000, '十万':100000, '拾万':100000 \
        }
        self.numPointPattern = re.compile(u"(?:点|\.)")

    def numbertrans(self,numcn):
        split_cns = ["亿", "千万", "仟万", "百万", "佰万", "十万", "拾万", "万", "千", "仟", "佰", "百", "十", "拾"]
    
        if numcn.isdigit():
            #如果是数字，直接转为数字
            return int(numcn)
    
        #从最大的单位开始分割，然后 upper * 最大单位 + lower, 然后 upper 跟 lower 各自递归撒
        #如         二亿零四十万  ==   二 * 亿       + 零四十万
        for cn_num in split_cns:
            nums = numcn.split(cn_num)
            if len(nums) > 1:
                upper = self.numbertrans(nums[0])
                lower = self.numbertrans(nums[1])
                return upper * self.common_used_numerals[cn_num] + lower

        numcn_len = len(numcn)
        if numcn_len == 3:
            #刚好是一个字的时候，取字典内的数字
            return self.common_used_numerals[numcn]
        elif numcn_len > 3:
            #如果是多个字，[0-9]的汉字，直接转成相应的数字
            numcns = [t.encode("utf-8") for t in numcn.decode("utf-8")]
            nums = ""
            for _num in numcns:
                if _num.isdigit():
                    nums += _num
                    continue
                nums += str(self.common_used_numerals[_num])
            return int(nums)
        elif numcn_len == 0:
            return 0

    def numTransfrom(self,numstr):
        """
            数字转换。
        """
        num_cns = re.split(self.numPointPattern, numstr)
        if len(num_cns) == 1:
            pre_num = self.numbertrans(num_cns[0].encode('utf-8'))
            return int(pre_num)
        elif len(num_cns) == 2:
            pre_num = self.numbertrans(num_cns[0].encode('utf-8'))
            aft_num = float('0.' + str(self.numbertrans(num_cns[1].encode('utf-8'))))
            return pre_num + aft_num
        return None

#distance正则对象
class GdkSlotDistanceFind(object):
    """
        地址正则类。
    """
    def __init__(self,numextend,type1str,type2str):
        self.filterPattern = re.compile(u'万象城|南山海岸城|购物公园|附近|旁边|周围|这里|周边|不太远|公里|里|千米|k米|米|分钟|小时|分|步行|走路|开车|坐车|打车|乘车|打的|距离|路程|远近')
        unitstr = u'(?:公里|里|千米|k米|米)'
        modestr = u'(?:步行|走路|开车|坐车|打车|乘车|打的|骑车)'
        timestr = u'(?:分钟|小时|分)'
        headmarkstr = u'(?:距离|路程|远近)'
        tailmarkstr = u'(?:距离|路程|远近)'
        nonnumstr = u'[^\d一二三四五六七八九〇零十百千万亿]{0,3}?'

        self.patternStr = []
        self.patternStr.append(re.compile(u'(?:' + numextend + unitstr + u'?(?:到|至)' + numextend + unitstr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + nonnumstr + numextend + unitstr + u'?(?:到|至)' + numextend + u')'))
        self.patternStr.append(re.compile(u'(?:' + numextend + unitstr + u'?(?:到|至)' + numextend + nonnumstr + tailmarkstr + u')'))
        self.patternStr.append(re.compile(u'(?:' + modestr + nonnumstr + numextend + timestr + u'?(?:到|至)' + numextend + timestr + u')'))
        self.patternStr.append(re.compile(u'(?:' + numextend + timestr + u'?(?:到|至)' + numextend + timestr + modestr + u')'))
        self.patternStr.append(re.compile(u'(?:' + type1str + nonnumstr + numextend + unitstr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + modestr + type1str + nonnumstr + numextend + timestr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + type1str + nonnumstr + numextend + timestr + modestr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + type1str + nonnumstr + numextend + nonnumstr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + type1str + nonnumstr + numextend + nonnumstr + type2str + tailmarkstr + u')'))
        self.patternStr.append(re.compile(u'(?:附近|周围|旁边|这里|周边|不太远)'))

#price正则对象
class GdkSlotPriceFind(object):
    """
        地址正则类。
    """
    def __init__(self,numextend,numstr,type1str,type2str):
        self.filterPattern = re.compile(u'元钱|块钱|元|块|价格|价钱|单价|消费|每人|人均|价位|价码|金额|便宜')
        unitstr = u'(?:元钱|块钱|元|块)'
        perstr = numstr + u'(?:个人|人)'
        headmarkstr = u'(?:价格|价钱|单价|消费|每人|人均|价位|价码|金额)'
        tailmarkstr = u'(?:价格|价钱|单价|消费|每人|人均|价位|价码|金额)'
        nonnumstr = u'[^\d一二三四五六七八九〇零十百千万亿里米]{0,3}?'

        self.patternStr = []
        self.patternStr.append(re.compile(u'(?:' + numextend + unitstr + u'?(?:到|至)' + numextend + unitstr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + type1str + nonnumstr + numextend + unitstr + u'?(?:到|至)' + numextend + unitstr + u'?)'))
        self.patternStr.append(re.compile(u'(?:' + numextend + unitstr + u'?(?:到|至)' + numextend + unitstr + nonnumstr + tailmarkstr + u'?)'))
        self.patternStr.append(re.compile(u'(?:' + perstr + nonnumstr + numextend + unitstr + u'?(?:到|至)' + numextend + unitstr + '?' + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + perstr + type1str + nonnumstr + numextend + unitstr + '?' + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + type1str + nonnumstr + numextend + unitstr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + type1str + nonnumstr + numextend + nonnumstr + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + type1str + nonnumstr + numextend + nonnumstr + type2str + tailmarkstr + u')'))
        self.patternStr.append(re.compile(u'(?:便宜)'))#0-200

#attention正则对象
class GdkSlotAttentionFind(object):
    """
        地址正则类。
    """
    def __init__(self,numextend,type1str,type2str):
        self.filterPattern = re.compile(u'关注|关注度|关注量|访问|访问量|购买量|人流量|点击量|浏览|浏览量|喜欢度')
        headmarkstr = u'(?:关注|关注度|关注量|访问|访问量|购买量|人流量|点击量|浏览|浏览量|喜欢度)'
        tailmarkstr = u'(?:关注度|关注量|访问|访问量|购买量|人流量|点击量|浏览|浏览量|喜欢度)'
        nonnumstr = u'[^\d一二三四五六七八九〇零十百千万亿]{0,3}?'

        self.patternStr = []
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + nonnumstr + numextend + u'(?:到|至)' + numextend + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + numextend + u'(?:到|至)' + numextend + nonnumstr + tailmarkstr + u')'))
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + type1str + nonnumstr + numextend + type2str + u')'))
        self.patternStr.append(re.compile(u'(?:' + type1str + nonnumstr + numextend + type2str + nonnumstr + tailmarkstr + u')'))
        self.patternStr.append(re.compile(u'(?:' + headmarkstr + nonnumstr + u'(?:高|多|大))'))#500-1000

#XiaoI Slot抽取基础类
class XiaoiGdkSlot(object):
    """
        xiaoi slots抽取公共函数集。
    """
    def __init__(self):
        #数字查找、转换对象
        self.slotNumberFindObj = SlotNumberFind()
        #通用正则字串
        self.numstr = u"(?:\d|一|二|两|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
        self.numextend = self.numstr + u"+(?:(?:\.|点)" + self.numstr + "+){0,1}"
        self.type1str = u'(?:小于|不到|少于|只要|低于|不足|大于|高于|多于|不低于|不少于|不小于|不大于|不多于|不高于|超过|不超过)?'
        self.type2str = u'(?:以内|以外|之内|以下|以上|之上|左右|上下|范围内)?'
        #特定地址正则
        self.appointLocatePattern = re.compile(u'万象城|南山海岸城|购物公园')
        #单位抽取正则
        self.perPersonPattern = re.compile(u'(' + self.numstr + u')' + u'(?:个人|人)')
        self.numSplitPattern = re.compile(u'(?<!不)到|至')
        self.fuzzyLocatePattern = [re.compile(u'附近|周围|旁边|这里|周边|不太远'),re.compile(u'高|多|大'),re.compile(u'便宜'),re.compile(u'大概|大约')]
        #单位抽取正则
        self.modePattern = re.compile(u'步行|走路|开车|坐车|打车|乘车|打的')
        self.unitPattern = re.compile(u'(公里|里|千米|k米|米)|(?:(步行|走路|开车|坐车|打车|乘车|打的|骑车).*?(分钟|分|小时))|(?:(分钟|分|小时).*?(步行|走路|开车|坐车|打车|乘车|打的|骑车))')
        #范围标志正则
        self.rangeFlagPattern = re.compile(u'小于|不到|少于|只要|低于|不足|大于|高于|多于|范围内|不低于|不大于|不多于|不高于|不少于|不小于|以内|之内|以下|以上|以外|之上|左右|上下|超过|不超过')
        #价格扩展正则
        self.queryExtendFilterPattern,self.queryExtendNumPattern = self.getQueryExtendPattern()
        #slot抽取句式正则对象
        self.xiaoIGdkDistanceobj = GdkSlotDistanceFind(self.numextend,self.type1str,self.type2str)
        self.xiaoIGdkPriceobj = GdkSlotPriceFind(self.numextend,self.numstr,self.type1str,self.type2str)
        self.xiaoIGdkAttentionobj = GdkSlotAttentionFind(self.numextend,self.type1str,self.type2str)

    def getQueryExtendPattern(self):
        """
            构造价格扩展正则。
        """
        discount = u"折|折扣"
        price = u"元钱|块钱|元|块|价格|价钱|单价|消费|每人|人均|价位|价码|金额|便宜"
        distance = u"附近|旁边|周围|周边|这里|不太远|公里|里|千米|k米|米|分钟|小时|分|步行|走路|开车|坐车|打车|乘车|打的|距离|路程|远近"
        attention = u"关注|关注度|关注量|访问量|购买量|人流量|点击量|浏览|浏览量|喜欢度|访问"
        rating = u"评价|星"
        reputation = u"信用|诚信"
        others = u"其他"
        numre = re.compile(u"((?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿){2,5})")
        words = [discount, price, distance, attention, rating, reputation, others]
        _re = re.compile("(" + "|".join(words) + ")")
        return _re,numre

    def checkInput(self,queryobj):
        """
            校验输入参数。
        """
        if type(queryobj) is not unicode:
            query = queryobj.rawtext
        else:
            query = queryobj
        return query
    
    def priceQueryExtend(self,query):
        matchobj = re.search(self.queryExtendFilterPattern, query)
        if matchobj:
            return query
        return re.sub(self.queryExtendNumPattern, ur"\1块钱", query)

    def getDomainInfo(self,patternStr,query):
        """
            获取指定Slot的信息。
        """
        length = 0
        position = 0
        res = ''
        for pattern in patternStr:
            _obj = re.findall(pattern, query)
            if _obj:
                _obj = [_obj[-1]]
                resMatch = ''.join(_obj)
                temp_length = len(resMatch)
                temp_position = query.rfind(resMatch) + temp_length
                if temp_position > position:
                    length = temp_length
                    position = temp_position
                    res = resMatch
                elif temp_position == position and temp_length > length:
                    length = temp_length
                    position = temp_position
                    res = resMatch
        if res:
            return res
        else:
            return None

    def getLocate(self,query):
        """
            获得地址信息。
        """
        _obj = self.appointLocatePattern.search(query)
        if _obj:
            return _obj.group()
        else:
            return None

    def getNumber(self,mode,query):
        """
            获取数字信息。
        """
        #print query
        numList = []
        match = re.search(self.perPersonPattern,query)
        numBase = 1.0
        if match:
            numBase = 1.0/self.slotNumberFindObj.numTransfrom(match.group(1))
            query = query.replace(match.group(),'')
        queryList = re.split(self.numSplitPattern,query)
        if len(queryList) == 1:
            match = re.search(self.numextend,queryList[0])
            if match:
                num = self.slotNumberFindObj.numTransfrom(match.group())
                if type(num) == float:
                    if queryList[0].find(u'万') != -1:
                        num = num * 10000.0
                    elif queryList[0].find(u'千米') != -1:
                        num = num * 1000.0
                num = num * self.getUnit(queryList[0])*numBase
            else:
                if re.search(self.fuzzyLocatePattern[0],queryList[0]):
                    num = 500.0
                elif re.search(self.fuzzyLocatePattern[1],queryList[0]):
                    num = 500.0
                elif re.search(self.fuzzyLocatePattern[2],queryList[0]):
                    num = 200.0
            numList.append(num)
        elif len(queryList) == 2:
            #print queryList
            match = re.search(self.modePattern,queryList[0])
            if match:
                queryList[1] = match.group() + queryList[1]
            match1text = re.search(self.numextend,queryList[0]).group()
            num1 = self.slotNumberFindObj.numTransfrom(match1text)
            num1Base = self.getUnit(queryList[0])*numBase
            match2text = re.search(self.numextend,queryList[1]).group()
            num2 = self.slotNumberFindObj.numTransfrom(match2text)
            num2Base = self.getUnit(queryList[1])*numBase
            if type(num1) == float:
                if queryList[0].find(u'万') != -1:
                    num1Base = 10000.0
                elif queryList[0].find(u'千米') != -1:
                    num1Base = 1000.0
            if type(num2) == float:
                if queryList[1].find(u'万') != -1:
                    num2Base = 10000.0
                elif queryList[1].find(u'千米') != -1:
                    num2Base = 1000.0
            if (num1Base == 1.0) and (queryList[0].find(u'万') == -1) and (queryList[0].find(u'元') == -1) and (queryList[0].find(u'米') == -1):
                if mode != 'attention':
                    num1,num2 = self.checkRange(num1,num2,match1text,match2text)
                if num2Base != 1.0:
                    num1Base = num2Base
            numList.append(num1*num1Base)
            numList.append(num2*num2Base)
        return numList
        
    def checkRange(self,num1,num2,query0,query1):
        """
            校验范围(3到5百)
        """
        rate = 1.0
        num2_ = 0.0
        if query1.endswith(u'十'):
            rate = 10.0
            num2_ = num2/10.0
        elif query1.endswith(u'百'):
            rate = 100.0
            num2_ = num2/100.0
        elif query1.endswith(u'千') or query1.endswith(u'千米'):
            rate = 1000.0
            num2_ = num2/1000.0
        elif query1.endswith(u'万') != -1:
            rate = 10000.0
            num2_ = num2/10000.0
        elif query1.endswith(u'亿') != -1:
            rate = 100000000.0
            num2_ = num2/10000000.0
        else:
            rate = 1.0
        if num2_ > num1 and rate > 1:
            return num1*rate,num2
        return num1,num2

    def getUnit(self,query):
        """
            获取单位。
        """
        _obj = re.search(self.unitPattern,query)
        if _obj:
            unit_cn1 = _obj.group(1)
            unit_cn2 = _obj.group(2)
            unit_cn3 = _obj.group(3)
            unit_cn4 = _obj.group(4)
            unit_cn5 = _obj.group(5)
            if unit_cn1:
                if unit_cn1 in [u'公里',u'k米']:
                    return 1000.0
                elif unit_cn1 in [u'里']:
                    return 500.0
                elif unit_cn1 in [u'千米',u'米']:
                    return 1.0
            elif unit_cn2:
                num = 1.0
                if unit_cn2 in [u'步行',u'走路']:
                    num = num* 30
                elif unit_cn2 in [u'骑车']:
                    num = num* 300
                else:
                    num = num * 500
                if unit_cn3 in [u'小时']:
                    num = num * 60
                return num
            elif unit_cn4:
                num = 1.0
                if unit_cn5 in [u'步行',u'走路']:
                    num = num* 30
                elif unit_cn5 in [u'骑车']:
                    num = num* 300
                else:
                    num = num * 500
                if unit_cn4 in [u'小时']:
                    num = num * 60
                return num
        return 1.0

    def getRangeFlag(self,query):
        """
            获取范围或期望标志。
        """
        res = 0
        _obj = re.search(self.rangeFlagPattern,query)
        if _obj:
            rangeText = _obj.group()
            if rangeText in [u'小于',u'不到',u'少于',u'只要',u'低于',u'范围内',u'不足',u'以内',u'之内',u'以下',u'不大于',u'不多于',u'不高于',u'不超过']:
                res = -1
            elif rangeText in [u'大于',u'超过',u'高于',u'多于',u'不低于',u'不少于',u'不小于',u'以上',u'之上',u'以外']:
                res = 1
        if res == 0: 
            if re.search(self.fuzzyLocatePattern[0],query):
                res = -1
            if re.search(self.fuzzyLocatePattern[3],query):
                res = 0
            elif re.search(self.fuzzyLocatePattern[1],query):
                res = 1
            if re.search(self.fuzzyLocatePattern[2],query):
                res = -1
        return res

    def main(self,query,patternStr,mode,maxValue):
        """
            抽取具体字段信息。
        """
        #返回值
        infoDict = {}
        res = {}
        #处理
        if mode == 'distance':
            locate = self.getLocate(query)
            if locate:
                infoDict['locate'] = locate
        queryMatch = self.getDomainInfo(patternStr,query)
        #print 'queryMatch:',queryMatch
        if queryMatch:
            numList = self.getNumber(mode,queryMatch)
            if len(numList) == 2:
                infoDict['lowest'] = float(numList[0])
                infoDict['highest'] = float(numList[1])
            elif len(numList) == 1:
                rangeFlag = self.getRangeFlag(queryMatch)
                if rangeFlag == -1:
                    infoDict['lowest'] = float(0)
                    infoDict['highest'] = float(numList[0])
                elif rangeFlag == 0:
                    infoDict['excepted'] = float(numList[0])
                else:
                    infoDict['lowest'] = float(numList[0])
                    infoDict['highest'] = float(maxValue)
        #结果返回
        if infoDict:
            res[mode] = infoDict
            return res
        else:
            return None

xiaoIGdkSlotobj = XiaoiGdkSlot()
def Slotdistancefind(queryobj,maxDistance = 100000.0):
    """
        获取距离参数。
    """
    try:
        #输入校验
        query = xiaoIGdkSlotobj.checkInput(queryobj)
        if re.search(xiaoIGdkSlotobj.xiaoIGdkDistanceobj.filterPattern,query):
            return xiaoIGdkSlotobj.main(query,xiaoIGdkSlotobj.xiaoIGdkDistanceobj.patternStr,"distance",maxDistance)
    except:
        return None

def Slotpricefind(queryobj,maxPrice = 10000.0):
    """
        获取价格参数。
    """
    try:
        #输入校验
        query = xiaoIGdkSlotobj.checkInput(queryobj)
        query = xiaoIGdkSlotobj.priceQueryExtend(query)
        if re.search(xiaoIGdkSlotobj.xiaoIGdkPriceobj.filterPattern,query):
            return xiaoIGdkSlotobj.main(query,xiaoIGdkSlotobj.xiaoIGdkPriceobj.patternStr,"price",maxPrice)
    except:
        return None

def Slotattentionfind(queryobj,maxAttention = 1000.0):
    """
        获取关注度参数。
    """
    try:
        #输入校验
        query = xiaoIGdkSlotobj.checkInput(queryobj)
        if re.search(xiaoIGdkSlotobj.xiaoIGdkAttentionobj.filterPattern,query):
            return xiaoIGdkSlotobj.main(query,xiaoIGdkSlotobj.xiaoIGdkAttentionobj.patternStr,'attention',maxAttention)
    except:
        return None


if __name__=="__main__":
    start_time = time.time()
    for line in sys.stdin:
        line = line.strip().decode('utf-8')
        print line,'\t',Slotdistancefind(line),Slotattentionfind(line),Slotpricefind(line)
    print 'time elapsed:',time.time() - start_time,'s'
