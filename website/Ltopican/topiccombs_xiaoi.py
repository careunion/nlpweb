#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topiccombs_xiaoi.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-23 15:15:04
#########################################################################
import os
import json

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

#slot为空的是否要清空
def CombNonslotclear(queryobj, topic_obj=None):
    if not topic_obj:
        return None
    if type(topic_obj) is dict:
        topic_obj = [topic_obj]

    new_topic_obj = [ topic_dict for topic_dict in topic_obj if topic_dict.get("Slots", {})]

    if not new_topic_obj:
        return None
    return new_topic_obj 

#slot结果重组
def Combrestruct(queyrobj, topic_dict=None):
    if not topic_dict:
        return None
    if type(topic_dict) is not dict:
        return None
    domain = topic_dict["Domain"]
    score = topic_dict["Score"]
    intent = topic_dict["Intent"]
    slots = topic_dict["Slots"]
    domain_topics = {}
    for slotdict in slots.get("Topn", []):
        _domain = slotdict.get("categoryName", "") 
        if not domain_topics.has_key(_domain):
            domain_topics[_domain] = {}
        _dict = domain_topics.get(_domain, {}) 
        _dict["Domain"] = _domain
        _dict["Score"] = _dict.get("Score", 0.0) + slotdict.get("Score", 0.0)# * 0.5
        _dict["Intent"] = intent
        _dict["Slots"] = _dict.get("Slots", {})
        _dict["Slots"]["item_keyword"] = slotdict.get("item_keyword", "")
        _dict["Slots"]["store_keyword"] = slotdict.get("store_keyword", "")
        for k,v in slots.items():
            if k == "Topn":continue
            _dict["Slots"][k] = v
    #print json.dumps(domain_topics, ensure_ascii=False)
    topiclist = []
    for k,v in domain_topics.items():
        v["Score"] = min(v.get("Score", 0.0) * 0.3, 0.5)
        topiclist.append(v)
    #print json.dumps(topiclist, ensure_ascii=False)
    return sorted(topiclist, key=lambda x:x.get("Score", 0.0), reverse=True)

#catg2id
xiaoi_catg2id = {}
for line in open(pwd_path + "/data/catg2id"):
    catgid, catgname = line.strip().decode("utf-8").split("\t")
    xiaoi_catg2id[catgname] = catgid
def Combcatg2id(queryobj, topic_obj=None):
    if not topic_obj:
        return None
    if type(topic_obj) is dict:
        topic_obj = [topic_obj]
    for topic_dict in topic_obj:
        domain = topic_dict["Domain"]
        catgid = xiaoi_catg2id.get(domain, "")
        if catgid:
            topic_dict["categoryId"] = catgid
    return topic_obj

#qa使用的句子
def Combxiaoiqa(queryobj, topic_obj=None):
    if not topic_obj:
        return {"Suggestion":u"能服务"}#None
    if type(topic_obj) is dict:
        topic_obj = [topic_obj]
    for topic_dict in topic_obj:
        pass
    return topic_obj



if __name__=="__main__":
    print "new file"

