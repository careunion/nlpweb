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
        jieba.load_userdict("topicdat/zz")
        jieba.load_userdict("topicdat/sport")
        jieba.load_userdict("topicdat/eat")
        jieba.load_userdict("topicdat/drug")

        self.sport_words = set([word.strip().decode("utf-8") for word in open("topicdat/sport")])
        self.eat_words = set([word.strip().decode("utf-8") for word in open("topicdat/eat")])
        self.measure_words = set([word.strip().decode("utf-8") for word in open("topicdat/measure")])
        self.durg_words = set([word.strip().decode("utf-8") for word in open("topicdat/drug")])
        self.zz_words  = set([word.strip().decode("utf-8") for word in open("topicdat/zz")])
        self.time_words_re = "(" + "|".join([word.strip().decode("utf-8") for word in open("topicdat/time")]) + ")"
    
    def www_topic(self, query, topicword, topic):
        wordlist, postaglist = query
        words = "".join(wordlist)
        topic_str = ""
        #if (not topicword) or (not topic):
        #    return u"查询 其他"
        if re.search(u"(\d|一|二|三|四|五|六|七|八|九|零){2,5}", words) and re.search(u"(怎么样|怎样)", words):
            topic_str += u"结果效果 "
        if re.search(u"多少", words):
            topic_str += u"数量 "
        if re.search(u"(时候|几时)", words):
            topic_str += u"时间 "
        if re.search(u"是否|是不是", words):
            topic_str += u"是否 "
        if topicword.find("_") != 0 and re.search(u"(吃|喝|整|来|搞)", words) and not re.search(u"(早|中|晚|午|夜)", topicword):
            topic_str += u"禁忌 "
        if not topic_str:
            return u"查询 HOW,WHAT,WHERE"
        else:
            return u"查询 " + topic_str

    def announce_topic(self, query, topicword, topic):
        wordlist, postaglist = query
        postag_dict = {"m":"NUM", "a":"ADJ"}
        _wordlist = [word if postag not in postag_dict else postag_dict[postag] for word,postag in zip(wordlist, postaglist)]
        words = "".join(_wordlist)
        topic_str = ""
        #if (not topicword) or (not topic):
        #    return u"通知 其他"
        if topicword and re.search(u"(是|为|" + topicword + ").{0,3}NUMNUM", words):
            topic_str += u"数值 "
        elif re.search(u"(是|为).{0,3}NUMNUM", words):
            topic_str += u"数值 "
        if re.search(self.time_words_re, words):
            topic_str += u"时间 "
        if topicword and re.search( topicword + ".{0,3}ADJ", words):
            topic_str += u"形容 "

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
        for word in query[0]:
            _obj = re.search(u"(吃|喝|喂|饮)", word)
            if _obj:
                tag = "_" + _obj.group()
            if word in self.eat_words:
                tag = word
                break
        return tag

    def measure_topic1(self, query):
        tag = ""
        _query = "".join(query[0])
        for word in query[0]:
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
            topicword = self.eat_topic1(query)
            if topicword:
                topic = self.eat
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
        return topicword, topic

    def level2_topic(self, query, topicword = "", topic = ""):
        topic2 = self.child_topic(query, topicword, topic)
        return topic2

    def main(self, question):
        posseg_list = list(jieba.posseg.cut(question))
        wordlist = [list(p)[0] for p in posseg_list]
        poslist = [list(p)[1] for p in posseg_list]
        query = (wordlist, poslist)
        topicword, topic1 = self.level1_topic(query)
        topic2 = self.level2_topic(query, topicword, topic1)
        print ("%s\t%s\t%s\t%s"%(topic1, topicword, topic2, "".join(query[0]))).encode("utf-8")


if __name__=="__main__":
    _obj = Topic_Judge()
    for line in sys.stdin:
        line = line.strip()
        _obj.main(line)
