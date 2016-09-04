#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topicintent.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-09 12:26:10
#########################################################################
import topicquery
import re

class topicintent:
    def __init__(self):
        pass

    def judge(self, queryobj):
        postext = queryobj.postext
        poslist = [t[1] for t in postext]
        if "n" in poslist or "r" in poslist or "vn" in poslist:
            return True
        return False
    
    def intenttype(self, queryobj):
        query = queryobj.rawtext
        if type(query) is not unicode:
            query = query.decode("utf-8")
        if re.search(ur"(.{1,3})(不|没)\1", query):
            return "Ask"
        if re.search(ur"怎|怎么|怎的|怎样|怎么样|怎么着|如何|为什么|谁|何|什么|哪儿|哪里|在哪|几时|几|多少|呢|吗", query):
            return "Ask"
        else:
            return "Normal"


if __name__=="__main__":
    queryobj = topicquery.topicquery("我们吃饭可以吗")
    intentobj = topicintent()
    print intentobj.intenttype(queryobj)

