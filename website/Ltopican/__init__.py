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

class TopicAnl:
    def __init__(self, conf_xml):
        self.conf = []
        self.topicobjs = []
        self.topicexsitedobj = topicintent.topicintent()

        self.appdomains = {}

        self.only_rank1_domains = set()
        self.unuseless_domains = set()


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
            self.conf.append(_dict)
    
    def topic_gen(self):
        for conf in self.conf:
            self.topicobjs.append(topicbase.TopicBase(conf))
        return None

    def topicscomb(self, topics):
        topics = sorted(topics, key=lambda x:x.get("Score", 0.0), reverse=True)
        comb_topics_dict = {}
        for topic in topics:
            #print json.dumps(topic, ensure_ascii=False),"\n"
            domain = topic.get("Domain", "")
            if not comb_topics_dict.has_key(domain):
                comb_topics_dict[domain] = {}
            oldtopic = comb_topics_dict[domain]
            for k,v in topic.items():
                if k == "Score":
                    oldtopic[k] = min(oldtopic.get(k, 0.0) + v, 1.0)
                elif type(v) is dict:
                    old_v = oldtopic.get(k, {})
                    old_v.update(v)
                    oldtopic[k] = old_v
                elif not k in oldtopic:
                    oldtopic[k] = v

        newtopics = [v for k,v in comb_topics_dict.items()]
                    
        return sorted(newtopics, key=lambda x:x.get("Score", 0.), reverse=False) 

    def topicsfilter(self, lasttopic, topics):
        last_topic_score = -1.0
        max_topics_score = 0.0

        other_topics = []

        for topic in topics:
            if topic.get("Domain") == lasttopic.get("Domain"):
                last_topic_score = topic.get("Score", 0.0)
            else:
                max_topics_score = max([max_topics_score, topic.get("Score", 0.0)])
                other_topics.append(topic)

        all_topic_scores = [topic.get("Score", 0.0) for topic in topics]
        all_topic_scores.append(0)
        max_all_topic_score = max(all_topic_scores)
        
        #print " ".join(list(self.only_rank1_domains))
        #print max_topics_score, max_all_topic_score
        #用于过滤，某些必须处于rank1位置的domain，如果不处于rank1，直接过滤
        topics = [topic for topic in topics if not( topic.get("Domain", "") in self.only_rank1_domains and topic.get("Score", 0.0) < max_all_topic_score)]
        other_topics = [topic for topic in other_topics if not( topic.get("Domain", "") in self.only_rank1_domains and topic.get("Score", 0.0) < max_all_topic_score)]

        if last_topic_score >= max_topics_score - 0.2:
            return topics
        else:
            return other_topics

    #如果topic是一个dict，表示是top1的topic，但是如果是list，表示是topn的topic
    def topicappend(self, topics, topic):
        if type(topic) is list:
            for _topic in topic:
                topics.append(_topic)
        else:
            topics.append(topic)

    #获取上一topic，但是保证topic是有效的
    def lastusefultopic(self, lasttopics):
        for topic in lasttopics:
            print json.dumps(topic, ensure_ascii=False)
            domain = topic.get("Domain")
            if domain not in self.unuseless_domains:
                return topic
        return {}


    #主函数, 用于分析Topic的识别（包含对上一topic的处理），最后返回一个topiclist
    def main(self, query, appname, lasttopicdicts = []):
        queryobj = topicquery.topicquery(query)
        topics = []
        #无意图，则考虑以前的topic要加权
        query_has_topic = self.topicexsitedobj.judge(queryobj)

        #获取query的intent
        queryobj.intent = self.topicexsitedobj.intenttype(queryobj)

        #上一有效意图获取
        lasttopicdict = self.lastusefultopic(lasttopicdicts)

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
        #遍历意图
        for topicobj in topicobjs:
            #查看是否根据上一意图是否需要更新
            st1 = time.time()
            topic = topicobj.topicupdate(queryobj, lasttopicdict, query_has_topic)
            #如果不是上一意图对象，则直接获取topic
            if not topic:
                topic = topicobj.topicfuc(queryobj)
            #添加topic
            if topic:
                self.topicappend(topics, topic)
            st2 = time.time()
            #print "Domain", topicobj.domain, "Last", st2-st1
        topics = self.topicscomb(topics)
        stt2 = time.time()
        print "time Last", stt2 - stt1
        return self.topicsfilter(lasttopicdict, topics)






if __name__=="__main__":
    t = TopicAnl("look.xml")
    for line in sys.stdin:
        o = t.main(line.strip(), "xiaolan", {"Domain": u"天气", "Score": 0.4, "Intent": "Ask", "Slots": {"Date": u"下个礼拜四"}})
        print json.dumps(o, ensure_ascii=False)

