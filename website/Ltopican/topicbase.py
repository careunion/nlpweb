#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: __init__.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-06 14:41:53
#########################################################################
import os
import jieba
import jieba.posseg
import json
import re
import itertools
import time
import sys
from topicslots import *
from topiccombs import *
from topiccombs_xiaoi import *
from slotfuc_xiaoi import *
from xiaoi_xiaobai_slot_vr4 import *
from topiccombs_xiaoiqa import *
from xiaoi_gdk_slot_v3 import *
from slotfuc_weathercity import *
from xiaolan_gdk_slot import *
from xiaolan_xiaobai_time_slot import * 

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

class TopicBase:
    #根据传入的conf进行初始化参数
    #1，读取规则文件集合（词法、语法）rulepath
    #2, 读取slots所需要的函数名称  slots
    #3, 读取combines所需要的函数(也放在slot函数里)名称,combine，意思就是对抽取slot之后，对slot的信息进行整理，最后交给用户
    #4，domain，表示整体的意图名称。而fatherdomains表示当前domain可以兼容的上一topic
    def __init__(self, confobj):
        self.domain = confobj.get("domain", "")
        self.rulepath = confobj.get("rulepath", "")
        self.slots = confobj.get("slots", "").split(",")
        self.combines = confobj.get("combines", "").split(",")

        #fatherdomains默认包含自己domain
        self.fatherdomains = set(confobj.get("fatherdomain", "").split(","))
        self.fatherdomains.add(self.domain)

        #slot降权分数
        self.none_slot_weight  = 0.8

        self.topicword = {}
        self.topicwordre = {}
        self.topicsynre = {}
        self.topiccomre = {}

        self.slotfucs = []
        self.combfucs = []

        #Slot/Comb 函数
        self.slotcomb2dict = {
                "Slotnumberfind":Slotnumberfind,
                "Slotdatefind" : Slotdatefind, 
                "Slotcityfind" : Slotcityfind,
                "SlotplanClassify" : SlotplanClassify,
                "Slotbrandsearch": Slotbrandsearch,
                "Slotdiscountfind": Slotdiscountfind,
                "Slotpricefind": Slotpricefind,
                "Slotattentionfind": Slotattentionfind,
                "Slotratingfind": Slotratingfind,
                "Slotreputationfind": Slotreputationfind,
                "Slotdistancefind": Slotdistancefind,
                "Slotcouponfind": Slotcouponfind,
                "Slotsearchfind": Slotsearchfind,
                "Slotremindfind": Slotremindfind,
                "Slottimefind": Slottimefind,
                "Combweather": Combweather,
                "CombNonslotclear": CombNonslotclear,
                "Combrestruct":Combrestruct,
                "Combcatg2id": Combcatg2id,
                "Combxiaoiqa": Combxiaoiqa,
                "Combbasetopic": Combbasetopic,
                }
        
        self.ruleLoad()
        self.slotcombLoad()
                 

    def ruleLoad(self):
        if not self.rulepath:
            retopiccomree
        wordlines = []
        wordrelines = []
        synrelines = []
        comrelines = []
        
        _lines = None
        #规则文件读取
        for line in open(self.rulepath):
            if line.find("#gram1") == 0:
                _lines = wordlines
            elif line.find("#rule1") == 0:
                _lines = wordrelines
            elif line.find("#rule2") == 0:
                _lines = synrelines
            elif line.find("#rule3") == 0:
                _lines = comrelines
            else:
                _lines.append(line.strip())
        #字典加载,并且给定默认权重
        self.twoelementLoad(self.topicword, wordlines, 0.4)
        self.twoelementLoad(self.topicwordre, wordrelines, 0.5)
        self.twoelementLoad(self.topicsynre, synrelines, 0.5)
        self.twoelementLoad(self.topiccomre, comrelines, 0.5)

        #self.rulecombine(self.topicword)
        #self.rulecombine(self.topicwordre)
        #self.rulecombine(self.topicsynre)
        #self.rulecombine(self.topiccomre)

    def twoelementLoad(self, _dict = {}, lines = [], basescore=0.1):
        for line in lines:
            infos = line.strip().decode("utf-8").split()
            if len(infos) == 2:
                _dict[infos[0]] = float(infos[1])
            if len(infos) == 1:
                #默认权重0.1
                _dict[infos[0]] = basescore

    #按照配置文件的slot与combine，进行函数获取
    def slotcombLoad(self):
        #存放slot名字与slot函数名的对应
        for slot in self.slots:
            if slot in self.slotcomb2dict:
                self.slotfucs.append(self.slotcomb2dict.get(slot))
        #存放combine名字与slot函数名的对应
        for slot in self.combines:
            if slot in self.slotcomb2dict:
                self.combfucs.append(self.slotcomb2dict.get(slot))
        #如果是basedomain，预先添加Combbasetopic
        if "*" in self.fatherdomains:
            self.combfucs.append(self.slotcomb2dict.get("Combbasetopic"))

    def rulecombine(self, redict):
        _topicword = {}
        for _re, score in redict.items():
            if not _topicword.has_key(score):
                _topicword[score] = []
            _topicword[score].append(_re)
        redict = {}
        for k,v in _topicword.items():
            vs = "(" + "|".join(v) + ")"
            redict[vs] = k
        return redict


    def refuc(self, redict, query):
        topicscore = 0.0
        for _re, score in redict.items():
            if "." not in _re and "|" not in _re and "}" not in _re and "*" not in _re:
                if _re in query:
                    topicscore += float(score)
            elif re.search(_re, query):
                topicscore += float(score)
        return topicscore

    #rule1的使用函数（见rules/）
    def topicwordfuc(self, query):
        return self.refuc(self.topicword, query)
    #rule2的使用函数（见rules/）
    def topicwordrefuc(self, query):
        return self.refuc(self.topicwordre, query)
    #rule3的使用函数（见rules/）
    def topicsynrefuc(self, posseg):
        #posseg 为[pair(u'\u6211\u4eec', u'r'), pair(u'\u53bb', u'v'), pair(u'\u5403\u996d', u'v')]
        pos_str =  "".join([t[1] for t in posseg])
        return self.refuc(self.topicsynre, "".join(pos_str))

    #rule4的使用函数（见rules/），也是最复杂的匹配方法，窗口穷举法
    def topiccomrefuc(self, posseg):
        topicscore = 0.0
        #对query进行分段、保证能够快速匹配
        posseg_iter = []
        tem_posseg = []
        wordnum = len(posseg)
        _num = 0
        max_length = 10
        move_step = 2
        #遍历所有的词及词性，按照固定长度（15），移动窗口（2）进行移动
        while(_num < wordnum):
            word, pos = list(posseg[_num])
            #保证句子不是太长
            if pos == "x" and len(tem_posseg) > 1:
                posseg_iter += list(itertools.product(*tem_posseg))
                tem_posseg = []
            #对于句子过长的，则保持窗口移动固定长度
            elif len(tem_posseg) >= max_length:
                posseg_iter += list(itertools.product(*tem_posseg))
                tem_posseg = []
                _num = _num - (max_length - move_step)
            else:
                tem_posseg.append((word, "#-" + pos + "#"))
            _num += 1
        if tem_posseg:
            posseg_iter += list(itertools.product(*tem_posseg))
        posseg_iter_str = ["".join(k) for k in posseg_iter]
           
        for _re, score in self.topiccomre.items():
            for _posseg in posseg_iter_str:
                if re.search(_re, _posseg):
                    topicscore += score
                    break
        return topicscore

    #比较list[dict]形式的slot，看是否有新的信息
    def slotdiff(self, oldslot, newslot):
        difftag = False
        if (not oldslot) and (not newslot):
            return difftag

        oldslotdict = oldslot[0]
        for newslotdict in newslot:
            for k,v in newslotdict.items():
                if v:
                    oldv = oldslotdict.get(k, "")
                    if oldv != v:
                        difftag = True
        return difftag

    #根据topic识别的结果，进行相应结果重组（以及combine）
    def topicdict(self, queryobj, domain="", intent="", scores=0.0, slots=[], contexts = [[]]):
        _dict = {}
        _dict["Domain"] = domain
        _dict["Intent"] = intent
        _dict["Score"] = 1.0 if sum(scores) > 1.0 else sum(scores)
        _dict["Query"] = queryobj.rawtext
        _dict["Slots"] = {}
        for slot in slots:
            if not slot:
                continue
            for k,v in slot.items():
                _dict["Slots"][k] = v

        #对所有的comb函数进行处理
        for combfuc in self.combfucs:
            _dict = combfuc(queryobj, _dict, contexts)
            if not _dict:
                return None

        #区分是一个list，还是单独的一个topic
        if type(_dict) is list:
            for tem_dict in _dict:
                tem_dict["_stamp"] = time.time()
        else:
            _dict["_stamp"] = time.time()
        return _dict

    #基础topic识别函数
    def topicfuc(self, queryobj, contexts=[[]], justscore = False):

        score1 = self.topicwordfuc(queryobj.rawtext)
        score2 = self.topicwordrefuc(queryobj.rawtext)
        score3 = self.topicsynrefuc(queryobj.postext)
        score4 = self.topiccomrefuc(queryobj.postext)
        topic_scores = [score1, score2, score3, score4]

        if justscore:
            return sum(topic_scores)

        if sum(topic_scores) > 0:
            #slots抽取
            slots = []
            for slotfuc in self.slotfucs:
                slotresult = slotfuc(queryobj)
                if slotresult:
                    slots.append(slotresult)
            slot_benefit_score = 0.1 if slots else 0.0
            #slot-有无-调权:无slot，则降权值
            if not slots:
                topic_scores = [score * self.none_slot_weight for score in topic_scores]
            topic_scores.append(slot_benefit_score)
            return self.topicdict(queryobj, self.domain, queryobj.intent, topic_scores, slots, contexts)
        return None

    #针对所有的context进行更新
    def contextupdate(self, queryobj, contexts, query_has_topic = False):
        topics = []
        searched_domains = set()
        for contextid in range(len(contexts)):
            context = contexts[contextid]
            maxscore = max([topic.get("Score", 0.0) for topic in context])
            lasttopicweight = 0.2 if contextid == 0 else 0.05
            for lasttopic in context:
                #只是保留最大分值一定范围(暂时0.1)的那些而已
                if lasttopic.get("Score", 0.0) < maxscore - 0.2:
                    continue
                if lasttopic.get("Domain", "") in searched_domains:
                    continue
                searched_domains.add(lasttopic.get("Domain", ""))
                topicobj = self.topicupdate(queryobj, lasttopic, lasttopicweight, query_has_topic)
                if topicobj:
                    if type(topicobj) is not list:
                        topicobj = [ topicobj ]
                    for t in topicobj:
                        topics.append(t)
                        print "\t lasttopic", lasttopic["Domain"], self.domain, t["Score"]
        return topics


    #针对上一topic的特别识别方法
    def topicupdate(self, queryobj, lasttopicdict, lasttopicweight = 0.2, has_topic = False):
        lasttopic_domain = lasttopicdict.get("Domain", "")
        if not lasttopic_domain:
            return None
        #当前topic识别对象必须在fatherdomains里面，才可以使用上一topic
        basedomain = "*" in self.fatherdomains
        sondomain = lasttopic_domain in self.fatherdomains
        if (not basedomain) and (not sondomain):
            return None
        #如果与上一意图的时间相隔太大5min，也不使用上一topic
        if time.time() - lasttopicdict.get("_stamp", 0) > 300:
            return None

        slots = [lasttopicdict.get("Slots")]
        _slots = []
        for slotfuc in self.slotfucs:
            slotresult = slotfuc(queryobj)
            if slotresult:
                slots.append(slotresult)
                _slots.append(slotresult)

        #slot有无， slot有无更新 的 tag
        has_slot_tag = True if _slots else False
        has_diff_slot_tag = self.slotdiff([lasttopicdict.get("Slots")], _slots)

        #根据当前query与上一topic进行当前topic分值预估
        newlasttopicscore = self.topicfuc(queryobj, lasttopicdict, True)
        if not has_slot_tag:
            newlasttopicscore = newlasttopicscore * self.none_slot_weight
        has_topic_score = 0.1 if not has_topic else 0.0

        has_slot_score = 0.05 if has_slot_tag else 0.0
        has_slot_score = 0.1 if has_slot_tag and not has_topic else has_slot_score
        has_diff_slot_score = 0.05 if has_diff_slot_tag else 0.0
        has_diff_slot_score = 0.1 if has_diff_slot_tag and not has_topic else has_diff_slot_score
        new_score = lasttopicdict.get("Score") * lasttopicweight + newlasttopicscore + has_topic_score + has_slot_score + has_diff_slot_score

        #如果是基础域，即score最大仅能为0.05
        if basedomain:
            new_score = min(new_score, 0.05 + new_score/100)

        #domain完全一致时，slot无变化，表明上一topic关联失败：
        if (not has_slot_tag) and lasttopic_domain == self.domain and newlasttopicscore == 0.0:# and queryobj.rawtext != lasttopicdict.get("Query", ""):
            return None

        #domain不一致时，无法识别为当前domain，表明上一topic关联失败
        if lasttopic_domain != self.domain and newlasttopicscore == 0.0:
            return None

        return self.topicdict(queryobj, self.domain, queryobj.intent, [new_score], slots, [[lasttopicdict]] )


if __name__=="__main__":
    conf_obj = {"domain":"test", "rulepath":"rules/rule2"}
    _obj = TopicBase(conf_obj)
    for line in sys.stdin:
        _obj.topicfuc(line.strip().decode("utf-8"))

