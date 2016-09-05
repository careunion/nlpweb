#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topicanl.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-09 10:54:20
#########################################################################
import xml.dom.minidom
import topicbase
import time
import topicquery
import topicintent
import json
import sys
import topicquestion
import random
import topicrobotask

class TopicAnl:
    def __init__(self, conf_xml):
        self.conf = []
        self.topicobjs = []
        self.topicexsitedobj = topicintent.topicintent()

        self.appdomains = {}

        self.only_rank1_domains = set()
        self.unuseless_domains = set()
        self.crosscontext_domains = set()

        self.robotask_apps = set()
        self.robotask_obj = topicquestion.topicquestion()

        self.conf_load(conf_xml)
        self.topic_gen()

    def conf_load(self, conf_xml):
        dom = xml.dom.minidom.parse(conf_xml)
        root = dom.documentElement
        #获取app需要识别的domain信息
        apps = root.getElementsByTagName("apps")
        for app in apps:
            username = ""
            domainnames = []
            if app.getElementsByTagName("appname"):
                username = app.getElementsByTagName("appname")[0].firstChild.data
            if app.getElementsByTagName("domainname"):
                domainnames = app.getElementsByTagName("domainname")[0].firstChild.data.split(",")
            if username and domainnames:
                self.appdomains[username] = domainnames
            if app.getElementsByTagName("robotasktask"):
                self.robotask_apps.add(username)
        #获取topic的信息
        items = root.getElementsByTagName("item")
        for item in items:
            _dict = {}
            if item.getElementsByTagName("domain"):
                _dict["domain"] = item.getElementsByTagName("domain")[0].firstChild.data
            else:
                continue
            if  item.getElementsByTagName("slots"):
                _dict["slots"] = item.getElementsByTagName("slots")[0].firstChild.data
            if item.getElementsByTagName("combines"):
                _dict["combines"] = item.getElementsByTagName("combines")[0].firstChild.data
            if item.getElementsByTagName("rulepath"):
                _dict["rulepath"] = item.getElementsByTagName("rulepath")[0].firstChild.data
            else:
                continue
            if item.getElementsByTagName("fatherdomain"):
                _dict["fatherdomain"] = item.getElementsByTagName("fatherdomain")[0].firstChild.data
            #only rank1 domains
            if item.getElementsByTagName("shouldrank1domains"):
                self.only_rank1_domains.add(_dict["domain"])
            if item.getElementsByTagName("unuselessdomain"):
                self.unuseless_domains.add(_dict["domain"])
            if item.getElementsByTagName("crosscontextdomains"):
                self.crosscontext_domains.add(_dict["domain"])
            self.conf.append(_dict)
    
    def topic_gen(self):
        for conf in self.conf:
            self.topicobjs.append(topicbase.TopicBase(conf))
        return None

    def topicscomb(self, topics):
        topics = sorted(topics, key=lambda x:x.get("Score", 0.0), reverse=True)
        comb_topics_dict = {}
        #print "----------------------"
        for topic in topics:
            print json.dumps(topic, ensure_ascii=False),"\n"
            domain = topic.get("Domain", "")
            if not comb_topics_dict.has_key(domain):
                comb_topics_dict[domain] = {}
            oldtopic = comb_topics_dict[domain]
            nulltopic = dict(oldtopic)
            for k,v in topic.items():
                if k == "Score":
                    oldtopic[k] = min(oldtopic.get(k, 0.0) + v, 1.0)
                elif type(v) is dict:
                    old_v = oldtopic.get(k, {})
                    v.update(old_v)
                    oldtopic[k] = v
                elif k not in oldtopic and not nulltopic:
                    oldtopic[k] = v

        newtopics = [v for k,v in comb_topics_dict.items()]
                    
        return sorted(newtopics, key=lambda x:x.get("Score", 0.), reverse=False) 

    def topicsfilter(self, topics, contexts):
        last_topic_score = -1.0
        max_topics_score = 0.0

        other_topics = []
        
        #获取以前所有有效context意图的domain
        context_domains = set()
        for context in contexts:
            for topic in context:
                context_domains.add(topic.get("Domain"))

        all_topic_scores = [topic.get("Score", 0.0) for topic in topics]
        all_topic_scores.append(0)
        max_all_topic_score = max(all_topic_scores)
        
        #用于过滤，某些必须处于rank1位置的domain，如果不处于rank1，直接过滤
        topics = [topic for topic in topics if not ( topic.get("Domain", "") in self.only_rank1_domains and topic.get("Score", 0.0) < max_all_topic_score)]
        #用于过滤，继承来的topic，但是不处于rank1的domain
        topics = [topic for topic in topics if not ( topic.get("Domain", "") in context_domains and topic.get("Score", 0.0) < max_all_topic_score)]

        return sorted(topics, key=lambda x:x.get("Score", 0.), reverse=True)

    #如果topic是一个dict，表示是top1的topic，但是如果是list，表示是topn的topic
    def topicappend(self, topics, topic):
        if type(topic) is list:
            for _topic in topic:
                topics.append(_topic)
        else:
            topics.append(topic)

    #获取所有有效的context信息，但是保证topic是有效的
    #就是寻找上一个topic，以及可以跨context继承的domain
    def usefulcontextsGen(self, contexts):
        usefulcontexts = []
        sensecontexts = []

        for contextid in range(len(contexts)):
            context = contexts[contextid]
            newcontext1 = [ topic for topic in context if topic.get("Domain", "") not in self.unuseless_domains]
            newcontext2 = [ topic for index, topic in enumerate(newcontext1) if topic.get("Domain", "") in self.crosscontext_domains or (index == 0 and not usefulcontexts)]
            if newcontext1:
                sensecontexts.append(newcontext1)
            if newcontext2:
                usefulcontexts.append(newcontext2)
        #print json.dumps(usefulcontexts, ensure_ascii=False)
        return sensecontexts, usefulcontexts 


    #主函数, 用于分析Topic的识别（包含对上一topic的处理），最后返回一个topiclist
    def topicmain(self, query, appname, usefulcontexts = []):
        queryobj = topicquery.topicquery(query)
        topics = []
        #无意图，则考虑以前的topic要加权
        query_has_topic = self.topicexsitedobj.judge(queryobj)
        queryobj.hastopic = query_has_topic

        #获取query的intent
        queryobj.intent = self.topicexsitedobj.intenttype(queryobj)

        #app平台级别用户意图
        topicobjs = []
        if appname in self.appdomains:
            appdomains = self.appdomains.get(appname, [])
            for topicobj in self.topicobjs:
                if topicobj.domain in appdomains:
                    topicobjs.append(topicobj)
        else:
            topicobjs = self.topicobjs

        stt1 = time.time()
        domaintimes = []
        #遍历意图
        for topicobj in topicobjs:
            #查看是否根据上一意图是否需要更新
            st1 = time.time()
            topic = topicobj.contextupdate(queryobj, usefulcontexts, query_has_topic)
            st2 = time.time()
            #如果不是上一意图对象，则直接获取topic
            if not topic:
                topic = topicobj.topicfuc(queryobj, usefulcontexts)
                
            #添加topic
            if topic:
                self.topicappend(topics, topic)
            #domaintimes.append((st2-st1, "Domain", topicobj.domain, "Last"))
        topics = self.topicscomb(topics)
        stt2 = time.time()
        print "time Last", stt2 - stt1
        return self.topicsfilter(topics, usefulcontexts)

    def main(self, query, appname, contexts = []):
        #对context进行筛选，选择可以继承的context
        sensecontexts, usefulcontexts = self.usefulcontextsGen(contexts)

        if appname in self.robotask_apps:
            topicrobotask.robotaskpre(query, appname, self.robotask_obj, self.robotask_apps, sensecontexts, usefulcontexts)

        alltopics = self.topicmain(query, appname, usefulcontexts)

        if appname in self.robotask_apps:
            topicrobotask.robottaskpost(query, appname, self.robotask_apps, alltopics, usefulcontexts)

        return alltopics







if __name__=="__main__":
    t = TopicAnl("look.xml")
    for line in sys.stdin:
        o = t.main(line.strip(), "xiaolan", {"Domain": u"天气", "Score": 0.4, "Intent": "Ask", "Slots": {"Date": u"下个礼拜四"}})
        print json.dumps(o, ensure_ascii=False)

