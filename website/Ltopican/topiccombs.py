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
from slotfuc_weather import *
import json

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

def Combweather(queryobj, topic_dict={}, contexts = [[]]):
    if not topic_dict:
        return None
    slot_dict = topic_dict.get("Slots", {})
    slot_dict["Weather"] = {}
    weatherdict = WeatherUrl(slot_dict.get("City",""), slot_dict.get("Days_r", 0))
    if not weatherdict:
        return topic_dict 
    for k,v in weatherdict.items():
        slot_dict["Weather"][k] = v
    return topic_dict


def Combbasetopic(queryobj, topic_obj={}, contexts = [[]]):
    if not topic_obj:
        return None
    if type(topic_obj) is dict:
        topic_obj = [topic_obj]
    if (not contexts) or (not contexts[0]):
        return topic_obj
    
    lasttopic = contexts[0][0]

    last_domain = lasttopic.get("Domain", "")
    last_catgid = lasttopic.get("categoryId", "")
    if not last_domain:
        return topic_obj
    
    for topic in topic_obj:
        topic["Domain"] = last_domain
        if last_catgid:
            topic["categoryId"] = last_catgid

    #不可继承的，都弄成topic的key
    topic["Cnonsense"] = 1

    return topic_obj
