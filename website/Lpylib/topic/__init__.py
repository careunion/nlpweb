#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topic_judge.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2016-04-20 11:13:28
#########################################################################
import re
import math
import sys
import jieba
import jieba.posseg
import os
import time

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

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

def numberfind(cn_str):
    if type(cn_str) is unicode:
        cn_str = cn_str.encode("utf-8")
    numstr = "(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
    numre = re.compile(numstr + "+(?:(?:\.|点)" + numstr + "+){0,1}")
    _obj = re.findall(numre, cn_str)
    if not _obj:
        return []
   
    num_list = []
    for num_cn in _obj:
        num_cns = re.split("(?:点|\.)", num_cn)
        if len(num_cns) == 1:
            pre_num = numbertrans(num_cns[0])
            num_list.append( str(pre_num)  )
        elif len(num_cns) == 2:
            pre_num = numbertrans(num_cns[0])
            aft_num = numbertrans(num_cns[1])
            num_list.append( str(pre_num) + "." + str(aft_num) )
    return num_list

class Topic_Judge:
    def __init__(self):
        self.sport_words = []
        self.eat_words = []
        self.measure_words = []
        self.drug_words = []
        self.zz_words = []
        
        self.drug = u"药品"
        self.eat = u"饮食"
        self.measure = u"测量"
        self.sport = u"运动"
        self.zz = u"症状"
        self.www_words = set(u"怎|怎么|怎的|怎样|怎么样|怎么着|如何|为什么|谁|何|什么|哪儿|哪里|在哪|几时|几|多少|？|?|呢|吗".split("|"))
        self.time_words_re = ""

        self.data_load()



    def data_load(self):
        jieba.load_userdict(pwd_path + "/topicdat/zz")
        jieba.load_userdict(pwd_path + "/topicdat/sport")
        jieba.load_userdict(pwd_path + "/topicdat/eat")
        jieba.load_userdict(pwd_path + "/topicdat/drug")

        self.sport_words = set([word.strip().decode("utf-8") for word in open(pwd_path + "/topicdat/sport")])
        self.eat_words = set([word.strip().decode("utf-8") for word in open(pwd_path + "/topicdat/eat")])
        self.measure_words = set([word.strip().decode("utf-8") for word in open(pwd_path + "/topicdat/measure")])
        self.durg_words = set([word.strip().decode("utf-8") for word in open(pwd_path + "/topicdat/drug")])
        self.zz_words  = set([word.strip().decode("utf-8") for word in open(pwd_path + "/topicdat/zz")])
        self.time_words_re = "(" + "|".join([word.strip().decode("utf-8") for word in open(pwd_path + "/topicdat/time")]) + ")"
    
    def www_topic(self, query, topicword, topic):
        wordlist, postaglist = query
        words = "".join(wordlist)
        topic_str = ""
        postag_dict = {"m":"NUM", "a":"ADJ"}
        _wordlist = [word if postag not in postag_dict else postag_dict[postag] for word,postag in zip(wordlist, postaglist)]
        #if (not topicword) or (not topic):
        #    return u"查询 其他"
        if re.search(u"(\d|一|二|三|四|五|六|七|八|九|零|\.){2,5}", words) and re.search(u"(怎么样|怎样|行|可以|好|中不|问题|事|关系|对|得当|适合|是否|是不是|正常|ok)", words):
            topic_str += u"数值 "
        if topicword and re.search(u"(是|为|" + topicword + ").{0,3}NUM", "".join(_wordlist)):
            topic_str += u"数值 "
        elif re.search(u"(是|为).{0,3}NUMNUM", "".join(_wordlist)):
            topic_str += u"数值 "

        if re.search(u"多少", words):
            topic_str += u"数目 "
        if re.search(u"(时候|几时)", words):
            topic_str += u"时间 "
        if re.search(u"是否|是不是", words):
            topic_str += u"是否 "
        if topicword.find("_") != 0 and re.search(u"(吃|喝|整|来|搞)", words) and not re.search(u"(早|中|晚|午|夜)", topicword):
            topic_str += u"禁忌 "
        if re.search(u"(测|量|查).{0,3}(过|了|完|啦)", words) or re.search(topicword + u".{0,5}是.{0,10}(正常|高|低)", words) or re.search(topicword + u".{0,10}(正常|高|低).{0,3}(吗|呢)", words)  or re.search(u"(已经|早就|好早).{0,5}(测|量|查)", words):
            topic_str += u"测了"

        if not topic_str:
            return u"查询 HOW,WHAT,WHERE"
        else:
            return u"查询 " + topic_str

    def www_judge(self, query):
        if re.search(u"(怎么样|怎样|多少|好不好|好不|吗$|嘛$|什么|问题|是否|是不是)", words):
            return True
        return False

    def announce_topic(self, query, topicword, topic):
        wordlist, postaglist = query
        postag_dict = {"m":"NUM", "a":"ADJ"}
        _wordlist = [word if postag not in postag_dict else postag_dict[postag] for word,postag in zip(wordlist, postaglist)]
        words = "".join(_wordlist)
        topic_str = ""
        #if (not topicword) or (not topic):
        #    return u"通知 其他"
        if topicword and re.search(u"(是|为|" + topicword + ").{0,3}NUM", words):
            topic_str += u"数值 "
        elif re.search(u"(是|为).{0,3}NUMNUM", words):
            topic_str += u"数值 "
        if re.search(self.time_words_re, words):
            topic_str += u"时间 "
        if topicword and re.search( topicword + ".{0,3}ADJ", words):
            topic_str += u"形容 "
        if re.search(u"(测|量|查).{0,3}(过|了|完|啦)", words) or re.search(u"(已经|早就|好早).{0,5}(测|量|查)", words):
            topic_str += u"测了"

        if topicword.find("_") != 0 and re.search(u"(吃|喝|整|来|搞)", words) and not re.search(u"(早|中|晚|午|夜)", topicword):
            topic_str += u"禁忌 "
        if not topic_str:
            return u"通知 其他"
        else:
            return u"通知 " + topic_str

    def child_topic(self, query, topicword, topic):
        wordlist, postaglist = query
        www_tag = 0
        words = "".join(wordlist)
        for word in self.www_words:
            if word in words:
                www_tag = 1
                break
        if re.search(u"(可.{0,2}不可|好.{0,2}不好|行.{0,2}不行|能.{0,2}不能|会{0,2}不会|有.{0,2}没有|可否|能否|行否|会否|好不$|行不$|能.{0,2}不$|可以.{0,2}不$|是否)", words):
            www_tag = 1
        if www_tag :
            topic = self.www_topic(query, topicword, topic)
        else:
            topic = self.announce_topic(query, topicword, topic)
        return topic


    def drug_topic1(self, query):
        tag = ""
        for word in query[0]:
            if u"药" in word:
                tag = u"药"
                break
            elif word in self.durg_words:
                tag = word
                break
        return tag

    def eat_topic1(self, query):
        tag = ""
        #print "_".join(query[0])
        for word in query[0]:
            _obj = re.search(u"(进食|吃|喝|喂|饮|(整|搞|来).{0,2}(点|些))", word)
            if _obj and not tag:
                tag = "_" + _obj.group()
            if word in self.eat_words:
                tag = word
                break
        return tag

    def measure_topic1(self, query):
        tag = ""
        _query = "".join(query[0])
        for word in query[0]:
            _obj = re.search(u"(血压|血糖)", word)
            if _obj:
                tag = _obj.group()
                break
            if word in self.measure_words:
                tag = word
                break
        if re.search(u"(测|量|验|查)(?!试).{0,3}(下)", _query):
            tag = u"测"
        return tag

    def sport_topic1(self, query):
        tag = ""
        _query = "".join(query[0])

        for word in query[0]:
            if word in self.sport_words:
                tag = word
        if re.search(u"(动|走|玩).*?(下)", _query):
            tag = u"运动"
        return tag

    def zz_topic1(self, query):
        tag = ""
        for word in query[0]:
            if word in self.zz_words:
                tag = word
        return tag

    #query  [0]:word list [1]:postag list
    def level1_topic(self, query):
        topic = ""
        topicword = ""
        if not topic:
            topicword = self.drug_topic1(query)
            if topicword:
                topic = self.drug
        if not topic:
            topicword = self.measure_topic1(query)
            if topicword:
                topic = self.measure
        if not topic:
            topicword = self.sport_topic1(query)
            if topicword:
                topic = self.sport
        if not topic:
            topicword = self.zz_topic1(query)
            if topicword:
                topic = self.zz
        if not topic:
            topicword = self.eat_topic1(query)
            if topicword:
                topic = self.eat
        return topicword, topic

    def level2_topic(self, query, topicword = "", topic = ""):
        topic2 = self.child_topic(query, topicword, topic)
        return topic2
    
    def xuetang(self, query, number = 0):
        par1 = ""
        par2 = ""
        par3 = ""
        wordlist, poslist = query
        timestr = time.strftime("%H %M",time.localtime(time.time()))
        hour, mins = timestr.split()
        hour = int(hour)
        mins = int(mins)

        if hour >= 4 and hour <= 10:
            par1 = "早上"
        elif hour >= 11 and hour <= 14:
            par1 = "中午"
        elif hour >= 15 and hour <= 20:
            par1 = "晚上"
        else:
            par1 = "半夜"

        eatword = self.eat_topic1(query)
        words = "".join(wordlist)
        if eatword:
            if re.search(u"(没|尚未|等|待|过|想|马上|立刻).{0,7}" + eatword.strip("_"), words):
                par2 = "餐前"
            elif (eatword.find("_") == 0 and re.search(eatword.strip("_") + u".{0,3}(完|过|了)", words) ) or re.search(u"(吃|喝|喂|饮|整|来|搞).{0,3}(完|过|了).{0,3}" + eatword, words) or re.search(u"(吃|喝|喂|饮|整|来|搞).{0,5}" + eatword + u".{0,3}了", words) or re.search(u"(已经)" + eatword.strip("_"), words):
                if not u"想" in words:
                    par2 = "餐后"
                #else:
                #    par2 = "餐中"
            if re.search(u"(喝|饮)水", words):
                par2 = ""
        if re.search(u"((餐|饭).{0,3}前|空腹|饿肚子|空肚子)", words):
            par2 = "餐前"
        if re.search(u"((餐|饭).{0,3}后|饱腹|饱了)", words):
            par2 = "餐后"

        if number:
            par3 = str(numberfind("".join(wordlist))[-1])

        return "|".join([par1, par2, par3])


    def large_topic(self, query):
        if re.search(u"(温度|天气|气温|下雨)", query):
            if self.www_judge(query):
                return "天气", "查询"
            else:
                return "天气", "通知"
        return None

    def maintopic(self, question):
        topic = self.large_topic(question)
        if topic:
            return topic

        posseg_list = list(jieba.posseg.cut(question))
        wordlist = [list(p)[0] for p in posseg_list]
        poslist = [list(p)[1] if not re.search("[\d.]", list(p)[0]) else "m" for p in posseg_list]
        query = (wordlist, poslist)
        topicword, topic1 = self.level1_topic(query)
        topic2 = self.level2_topic(query, topicword, topic1)
        topic2 = "%s\t%s\t%s"%(topic1, topicword, topic2)

        if u"测量" in topic2 and u"血糖" in topic2 and u"数值" in topic2:
            return u"血糖", "测量"
        elif u"测量" in topic2 and u"血糖" in topic2 and u"测了" in topic2:
            return u"血糖", "测量"

        if u"饮食" in topic2 and u"禁忌" in topic2 and u"查询" in topic2:
            return "饮食", "禁忌"
        if u"饮食" in topic2 and u"禁忌" in topic2 and u"通知" in topic2:
            return "饮食", "禁忌"

        if len(re.sub(u"呢|吗|哟|的", "", question)) > 2:
            return "Others","Others"
        return None
    
    def main(self, query):
        topic = self.maintopic(query)
        if not topic:
            return topic
        else:
            domain, intent = topic
        topic_dict = {}
        topic_dict["Domain"] = domain
        topic_dict["Intent"] = intent
        topic_dict["Score"] = 0.9
        topic_dict["Slots"] = []
        return topic_dict
      
    
        
        

if __name__=="__main__":
    _obj = Topic_Judge()
    for line in sys.stdin:
        line = line.strip()
        t = _obj.main(line)
        print t[0], t[1]



