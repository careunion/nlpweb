#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: Lreq.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-07-12 13:51:02
#########################################################################
import time
import json
import sys 
reload(sys)
sys.path.append('..')
from ContextAPI import Context

obj_ContextAPI = Context()
class Lreq:

    #利用req的信息填充对象
    #字段依照设计文档
    def __init__(self, req_json = {}):
        self.Appid = req_json.get("Appid", "")
        self.Skey = req_json.get("Skey", "")
        self.Uid = req_json.get("Uid", "")
        self.Raw_text = req_json.get("Raw_text", "")
        self.Topic_topn = req_json.get("Topic_topn", 1)
        self.Simtext_topn = req_json.get("Simtext_topn", 1)
        self.Word_set = req_json.get("Word_set", [])
        self.Context_text = req_json.get("Context_text", [])
        self.Context_topic = req_json.get("Context_topic", [])
        self.Version = req_json.get("Version", "")
        self.Fuc_id = req_json.get("Fuc_id", "")

        self.Robot_question = req_json.get("Robot_question", "")

    #输出req信息到标准输出
    def pprint(self, logger):
        if not logger:
            print "self.Appid", self.Appid , "\t"
            print "self.Skey", self.Skey, "\t"
            print "self.Uid", self.Uid , "\t"
            print "self.Raw_text", self.Raw_text, "\t"
            print "self.Topic_topn", self.Topic_topn, "\t"
            print "self.Simtext_topn", self.Simtext_topn, "\t"
            print "self.Word_set", self.Word_set, "\t"
            print "self.Context_text", self.Context_text, "\t"
            print "self.Context_topic", self.Context_topic, "\t"
            print "self.Version", self.Version, "\t"
            print "self.Fuc_id", self.Fuc_id, "\t"
        else:
            outlist = ["Request Info:", self.Appid, self.Skey, self.Uid, self.Raw_text, self.Topic_topn, self.Simtext_topn, self.Word_set, self.Context_text, self.Context_topic, self.Version, self.Fuc_id, self.Robot_question]
            return json.dumps(outlist, ensure_ascii=False)


    #添加当前识别信息
    def append(self, topic):
        self.Context_text.append(self.Raw_text)
        self.Context_topic.append(topic)


class Appusers:

    #初始化平台级别用户信息(类似user-passwd)
    def __init__(self):
        self.appuserinfo = {} 

    #利用额外信息进行用户信息填充(暂用文件形式:user\tpasswd)
    def __init__(self, path):
        self.appuserinfo = {}
        for line in open(path):
            t1,t2 = line.strip().split("\t")
            self.appuserinfo[t1] = t2

    def certif(self, reqobj):
        if reqobj.Appid in self.appuserinfo and reqobj.Skey == self.appuserinfo[reqobj.Appid]:
            return True
        return False

class Requser:
    #用于做个性化或是多轮信息

    #存储基本信息
    def __init__(self, uid = "", text = [], topic = [],flag = True):
        self.uid = uid
        self.context_topics = []
        self.context_texts = []
        self.topic_flag = flag

        if topic:
            self.context_topics = topic
        if text:
            self.context_texts = text

    def append(self, text, topic):
        self.context_topics.insert(0, topic)
        self.context_texts.insert(0, text)
        self.context_topics = self.context_topics[:5]
        self.context_texts = self.context_texts[:5]
        self.topic_flag = True

    def pprint(self):
        print "self.uid", self.uid
        print "self.context_texts", "|".join(self.context_texts)
        print "self.context_topics", "|".join(self.context_topics)

    def save(self):
        #return self.uid + "\t" + self.context_texts[0] + "\t" + self.context_topics[0]
        #contextTopics = []
        #for item in self.context_topics:
        #    contextTopics += item
        return self.uid,[self.context_texts, self.context_topics,self.topic_flag]

class Requsers:
    #存储所有个性化的数据
    
    #从文本中读取信息
    def __init__(self):
        self.requsers = {}
        self.updatetime = time.time()
        contextDict = obj_ContextAPI.loadData()
        print "个数：",len(contextDict)
        for key,value in contextDict.items():
            #uid, text, topic
            t1 = key
            t2 = value[0]
            t3 = value[1]
            t4 = value[2]
            #print 't1:',t1
            #print 't2:',t2
            #print 't3:',t3
            #print 't4:',t4
            self.requsers[t1] = Requser(t1, t2, t3, t4)
    
    #context信息更新
    def append(self, reqobj):
        if not reqobj.Uid in self.requsers:
            self.requsers[reqobj.Uid] = Requser(reqobj.Uid)
        self.requsers[reqobj.Uid].append(reqobj.Context_text[-1], reqobj.Context_topic[-1])

        #调用更新数据
        #self.save()

    #存储起来
    def save(self):
        #十秒更新一次文本
        if self.updatetime > time.time() - 10:
            return
        self.updatetime = time.time()
        contextDict = {}
        for _uid, _requser in self.requsers.items():
            key,value = _requser.save()
            if value[2]:
                contextDict[key] = value
                self.requsers[_uid].topic_flag = False
        #print "Lreq:",json.dumps(contextDict,ensure_ascii = False)
        print "Context Saved"
        obj_ContextAPI.dumpData(contextDict)

    def pprint(self, reqobj):
        if reqobj.Uid in self.requsers:
            self.requsers[reqobj.Uid].pprint()
        else:
            print "INvalid User", reqobj.Uid
            
        

            

