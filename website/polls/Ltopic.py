#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: Ltopic.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-07-12 16:00:04
#########################################################################
#import Lpylib.topic as assist
import Ltopican
import json

topicobj = Ltopican.TopicAnl("conf/look.xml")
questionobj = Ltopican.topicquestion.topicquestion()
#返回topn的topic，如果无topic，也要返回一个空的dict
def topn_topics_get(reqobj, requsers_obj):
    #如果reqobj中有Robot_question，则表示用户来回答了问题
    if reqobj.Robot_question:
        return questionobj.main(reqobj.Raw_text, reqobj.Robot_question)

    #否则，则直接调用topic识别
    return topn_has_topic_get(reqobj, requsers_obj)

def topn_has_topic_get(reqobj, requsers_obj):
    query = reqobj.Raw_text
    if len(query.strip()) == 0:
        return None
    
    #获取上一个topic
    lasttopics = [] 
    if reqobj.Uid in requsers_obj.requsers and requsers_obj.requsers[reqobj.Uid].context_topics:
        lasttopics = requsers_obj.requsers[reqobj.Uid].context_topics#[0]

    if reqobj.Context_topic:
        lasttopics = reqobj.Context_topic
        lasttopics = [Ltopic(topic)._dict for topic in lasttopics]

    #根据appid， query，上一个topic，获取当前topic信息
    topics = topicobj.main(query, reqobj.Appid, lasttopics) 

    #取topn
    topics = sorted(topics, key=lambda x:x.get("Score", 0.0), reverse=True)[:reqobj.Topic_topn]
    return topics

class Ltopic:
    def __init__(self, domain = "", score = 0.5, intent = "", slots = []):
        _dict = {}
        _dict["Domain"] = domain
        _dict["Score"] = score
        _dict["Slots"] = slots
        _dict["Intent"] = intent
        self._dict = _dict

