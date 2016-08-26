#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topic_judge.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2016-04-20 11:13:28
#########################################################################
import os
import re
import math
import sys
import jieba
import jieba.posseg


pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
class SenJudge: 
    def __init__(self):
        self.Ddata_load()
        self.Ttrans_dict, self.Ppos_dict = self.Mmodel_load()
    def Ddata_load(self):
        jieba.load_userdict(pwd_path + "/../topicdat/zz")
        jieba.load_userdict(pwd_path + "/../topicdat/sport")
        jieba.load_userdict(pwd_path + "/../topicdat/eat")
        jieba.load_userdict(pwd_path + "/../topicdat/drug")
    
    def Mmodel_load(self):
        trans_dict = {}
        pos_dict = {}
        for line in open(pwd_path + "/topic_trans.model"):
            infos = line.split("\t")
            pos1 = infos[0].strip()
            pos2 = infos[2].strip()
            num = int(infos[3].strip())
    
            if not trans_dict.has_key(pos1):
                trans_dict[pos1] = {}
            trans_dict[pos1][pos2] = num
            pos_dict[pos1] = pos_dict.get(pos1, 0) +num
        trans_dict["m"]["m"] = 10217
        trans_dict["m"]["zg"] = 5217
        trans_dict["v"]["vg"] = 2000
        trans_dict["c"]["vg"] = 1000
        trans_dict["nr"]["nr"] = 1000
        trans_dict["n"]["q"] = 1000
        trans_dict["a"]["nr"] = 1000
        trans_dict["nr"]["a"] = 1000
        trans_dict["q"]["vn"] = 1000
        return trans_dict, pos_dict
    
    def sen_judge_main(self, line):
        line = line.decode("utf-8").strip()
        pos_list = [list(k)[1] if not re.search("[\d.]", list(k)[0]) else "m" for k in  list(jieba.posseg.cut(line, HMM=False)) ]
        if len(line) > 30:
            return 1
        elif len(line) == 1 and line not in u"嗯啊好恩哦对是哟":
            return 1
        elif len(line) == 1:
            return 0
        elif len(pos_list) < 2:
            return 0
        #print list(jieba.posseg.cut(line, HMM=False))
        log1 = 1
        log2 = 1
        for i in range(len(pos_list) - 1):
            _pos1 = pos_list[i]
            _pos2 = pos_list[i + 1]
            log1 = log1 * (self.Ttrans_dict.get(_pos1, {}).get(_pos2, 0) + 1) /10.0
            log2 = log2 * (self.Ppos_dict.get(_pos1, 0) + 30) / 10.0
            #print _pos1, _pos2, (self.Ttrans_dict.get(_pos1, {}).get(_pos2, 0) + 1), (self.Ppos_dict.get(_pos1, 0) + 30)
        p = (math.log(log1) - math.log(log2)) * 1.0/len(line)
        p = min(1.0, max(p/2 + 1.5, 0))
        #print line, p
        return 1-p#0#, p
    
if __name__=="__main__":
    _obj = SenJudge() 
    for line in sys.stdin:
        t = _obj.sen_judge_main(line)
        print line.strip(), t
