#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topicquery.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-09 11:33:42
#########################################################################

import jieba
import jieba.posseg

class topicquery:
    def __init__(self, query):
        self.rawtext = query
        if self.rawtext is not unicode:
            self.rawtext = self.rawtext.decode("utf-8")
        self.segtext = list(jieba.cut(query))
        self.postext = [list(k) for k in jieba.posseg.cut(query)]
        self.lastquery = ""
        self.intent = ""

if __name__=="__main__":
    t = topicquery("我们吃饭吧")
    print t.segtext
    print t.postext

