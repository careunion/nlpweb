#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topiccombs_xiaoiqa.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-24 10:08:25
#########################################################################
import os
import sys
import random
import json
import re
import time

pwd = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

class xiaoiqa:
    def __init__(self, para_path = pwd + "/data/xiaoiqa_para", baseqa_path = pwd + "/data/xiaoiqa_baseqa", allcatg_path = pwd + "/data/xiaoiqa_catg", \
            domainqa_path = pwd + "/data/xiaoiqa_domainqa", catgqa_path = pwd + "/data/xiaoiqa_catgqa", catgokqa_path = pwd + "/data/xiaoiqa_catgokqa",\
            startsearch_path = pwd + "/data/xiaoiqa_gosearchqa", domainqa_catg_path = pwd + "/data/xiaoiqa_domaincatg"):
        self.para2name = {}
        self.baseqa = []
        self.catgs = set()
        self.domainqa = {}
        self.domaincatgs = set()
        self.catgqa = {}
        self.catgokqa = {}
        self.startsearchqa = set()

        self.joinword = [u"还是", u"或是", u"?", u"呢？", u"或者", u"或"]
        self.search_re = u"(搜索|查.{0,3}下|搜.{0,3}下|查查|搜搜|检索|查询)"

        self.dictload(self.para2name, para_path)
        self.dictload(self.domainqa, domainqa_path)
        self.dictload(self.catgqa, catgqa_path)
        self.dictload(self.catgokqa, catgokqa_path)
        self.listload(self.baseqa, baseqa_path)
        self.setload(self.catgs, allcatg_path)
        self.setload(self.domaincatgs, domainqa_catg_path)
        self.setload(self.startsearchqa, startsearch_path)

    def setload(self, _set, path):
        for line in open(path):
            _set.add(line.strip().decode("utf-8"))

    def listload(self, _list, path):
        for line in open(path):
            _list.append(line.strip().decode("utf-8"))

    def dictload(self, _dict, path):
        for line in open(path):
            infos = line.strip().decode("utf-8").split(" ", 1)
            if len(infos) != 2:continue
            if infos[0] not in _dict:
                _dict[infos[0]] = infos[1].split()
            else:
                for tem in infos[1].split():
                    _dict[infos[0]].append(tem)

    def dictrandom(self, _dict):
        sortedkeys = sorted(_dict.keys())
        randtexts = [ random.sample(_dict[key], 1)[0] for key in sortedkeys]
        return randtexts

    def baseanswer(self, queryobj, topicobj, contexts = [[]] ):
        if re.search(self.search_re, queryobj.rawtext):
            topicobj["Slots"]["Gosearch"] = 1
            return random.sample(self.startsearchqa, 1)[0]

        topicobj["Slots"]["Gosearch"] = 0
        return random.sample(self.baseqa, 1)[0]

    def domainanswer(self):
        twocatgs = random.sample(self.domaincatgs, 2)
        joinword = random.sample(self.joinword, 1)[0]
        catgs = joinword.join(twocatgs) + "?"

        startwords = u"要 查 看 找".split()
        catgs = random.sample(startwords, 1)[0] + catgs

        statictexts = self.dictrandom(self.domainqa)
        insertpos = 1#random.sample(range(2), 1)[0]
        statictexts.insert(insertpos, catgs)
        return "".join(statictexts)

    def catganswer(self, queryobj, topicdict):
        has_pars = set(topicdict.get("Slots", {}).keys())
        all_pars = set(self.para2name.keys())
        has_no_pars = all_pars - has_pars

        #如果获取到的参数已经足够多了，表示可以搜索了，Gosearch==1
        if len(all_pars) - len(has_no_pars) > 1:
            topicdict["Slots"]["Gosearch"] = 1
            return random.sample(self.startsearchqa, 1)[0]#u"开始搜索"

        #如果句子直接有搜索的含义，直接开始搜索
        if re.search(self.search_re, queryobj.rawtext) and len(all_pars) - len(has_no_pars) > 0:
            topicdict["Slots"]["Gosearch"] = 1
            return random.sample(self.startsearchqa, 1)[0]#u"开始搜索"

        #如果has_no_pars为空，表示需要是否直接返回一般句式
        topicdict["Slots"]["Gosearch"] = 0
        if not has_no_pars:
            statictexts = self.dictrandom(self.catgokqa)
            return  "".join(statictexts)
        else:
            statictexts = self.dictrandom(self.catgqa)
            pars = random.sample(has_no_pars, 1)[0]
            parnames = self.para2name[pars]
            parname = random.sample(parnames, 1)[0]
            statictexts.insert(2, parname)
            return  "".join(statictexts)

    def qamain(self, queryobj, topic_obj, contexts = [[]] ):
        if type(topic_obj) is not list:
            topic_obj = [topic_obj]
        for topic_dict in topic_obj:
            #print "++++"
            #print json.dumps(topic_dict, ensure_ascii=False)
            domain = topic_dict.get("Domain", "")
            answer = ""
            searchok = topic_dict["Slots"].get("Searchtag", 0)
            if domain == u"基础交互":
                answer = self.baseanswer(queryobj, topic_dict, contexts)
                searchok = searchok 
    
            if domain == u"商品":
                answer = self.domainanswer()
                searchok = 0
    
            if domain in self.catgs:
                answer = self.catganswer(queryobj, topic_dict)
                searchok = 1
            
            if answer:
                topic_dict["Slots"]["Suggestion"] = answer
                topic_dict["Slots"]["Searchtag"] = searchok
        #print answer
        #return answer
        return topic_obj

xiaoiqaobj = xiaoiqa()
Combxiaoiqa = xiaoiqaobj.qamain
        

#t_dict = {
#        "Domain":u"男上装",
#        "Slots":{
#            "price":1,
#            "discount":2,
#            "distance":1,
#            "rating":2,
#            "reputation":1,
#            "attention":4,
#            }
#        }
#obj = xiaoiqa()
#print obj.qamain(t_dict)
#
        

