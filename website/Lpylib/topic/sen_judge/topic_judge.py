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

def data_load():
    jieba.load_userdict("../topicdat/zz")
    jieba.load_userdict("../topicdat/sport")
    jieba.load_userdict("../topicdat/eat")
    jieba.load_userdict("../topicdat/drug")

if __name__=="__main__":
    data_load()
    trans_dict = {}
    num = 0
    for line in sys.stdin:
        num += 1
        line = line.decode("utf-8")
        line = line.strip(u"病情描述及疑问：")
        line = line.strip()
        lines = [re.sub(u"(，|。|,|;|、|\s|：|:|？|\?|？|\.)", "", line) ]
        for line in lines:
            #pos_list = [list(k)[1] for k in  list(jieba.posseg.cut(line, HMM=False)) ] 
            pos_list = [list(k)[1] if not re.search("[\d.]", list(k)[0]) else "m" for k in  list(jieba.posseg.cut(line, HMM=False)) ]
            if len(pos_list) < 2:continue
            #print line, pos_list
            for i in range(len(pos_list) - 1):
                _pos1 = pos_list[i]
                _pos2 = pos_list[i + 1]
                if not trans_dict.has_key(_pos1):
                    trans_dict[_pos1] = {}
                if not trans_dict[_pos1].has_key(_pos2):
                    trans_dict[_pos1][_pos2] = 0
                trans_dict[_pos1][_pos2] += 1

    pos_list = trans_dict.keys()
    for pos1 in pos_list:
        for pos2 in pos_list:
            print pos1, "\t->\t", pos2, "\t", trans_dict[pos1].get(pos2, 0)
        
        
