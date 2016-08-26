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
pwd = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

class xiaoiqa:
    def __init__(self, para_path = pwd + "/data/xiaoiqa_para", baseqa_path = pwd + "/data/xiaoiqa_baseqa", allcatg_path = pwd + "/data/xiaoiqa_catg", \
            domainqa_path = pwd + "/data/xiaoiqa_domainqa", catgqa_path = pwd + "/data/xiaoiqa_catgqa", catgokqa_path = pwd + "/data/xiaoiqa_catgokqa"):
        self.para2name = {}
        self.baseqa = []
        self.catgs = set()
        self.domainqa = {}
        self.catgqa = {}
        self.catgokqa = {}

        self.joinword = [u"还是", u"或是", u"?", u"或者", u"或"]

        self.dictload(self.para2name, para_path)
        self.dictload(self.domainqa, domainqa_path)
        self.dictload(self.catgqa, catgqa_path)
        self.dictload(self.catgokqa, catgokqa_path)
        self.listload(self.baseqa, baseqa_path)
        self.setload(self.catgs, allcatg_path)

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

    def domainanswer(self):
        twocatgs = random.sample(self.catgs, 2)
        joinword = random.sample(self.joinword, 1)[0]
        catgs = joinword.join(twocatgs) + "?"

        statictexts = self.dictrandom(self.domainqa)
        insertpos = random.sample(range(2), 1)[0]
        statictexts.insert(insertpos, catgs)
        return "".join(statictexts)

    def catganswer(self, topicdict):
        has_pars = set(topicdict.get("Slots", {}).keys())
        all_pars = set(self.para2name.keys())
        has_no_pars = all_pars - has_pars

        #如果has_no_pars为空，表示需要是否直接返回一般句式
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

    def qamain(self, queryobj, topic_obj):
        if type(topic_obj) is not list:
            topic_obj = [topic_obj]
        for topic_dict in topic_obj:
            domain = topic_dict.get("Domain", "")
            answer = ""
            searchok = 0
            if domain == u"基础交互":
                answer = random.sample(self.baseqa, 1)[0]
                searchok = 0
    
            if domain == u"商品":
                answer = self.domainanswer()
                searchok = 0
    
            if domain in self.catgs:
                answer = self.catganswer(topic_dict)
                searchok = 1
            
            if answer:
                topic_dict["Suggestion"] = answer
                topic_dict["Searchtag"] = searchok
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
        

