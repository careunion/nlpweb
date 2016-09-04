#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topicrobotask.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-09-01 16:30:31
#########################################################################
import random
import json


def robotaskpre(query, appname, robotask_obj, robotask_apps, sensecontexts, usefulcontexts):
    #表明当前app是不是需要robotask服务/功能 --- 前处理
    if appname in robotask_apps and sensecontexts:
        lastsensecontext = sensecontexts[0]
        #保证上一次，确实是RobotAsk的，而且上一次topic都有数据
        #print "========="
        #print json.dumps(lastsensecontext[0], ensure_ascii=False)
        if lastsensecontext and lastsensecontext[0] and lastsensecontext[0].get("RobotAsk", 0) and lastsensecontext[0]["Slots"].get("Suggestion", ""):
            answer = robotask_obj.main(query, lastsensecontext[0]["Slots"].get("Suggestion", ""))
            if answer and answer[0].get("Slots", {}).has_key("ChooseNum") and answer[0].get("Slots", {}).get("ChooseNum", -1) >= 0:
                if not usefulcontexts:
                    usefulcontexts.append([])
                #直接把最近有用的context的（lastsensecontext），选择的第choosenum个的topic放在useful第一个，这样就先继承他自己撒
                #而且里面的逻辑保证了，每个domain不会继承多次
                choosenum = answer[0].get("Slots", {})["ChooseNum"] - 1 
                usefulcontexts[0].insert(0, lastsensecontext[choosenum])
                #print choosenum
                #然后再对最近的context的分值有一定的调整
                for topic in usefulcontexts[0][1:]:
                    topic["Score"] = max(topic.get("Score") - 0.1, 0.0)
        #print json.dumps(usefulcontexts[0][0], ensure_ascii=False)

def robottaskpost(query, appname, robotask_apps, alltopics, usefulcontexts = []):
    #表明当前app是不是需要robotask服务/功能 --- 后处理
    if appname in robotask_apps and alltopics:
        maxscore = alltopics[0].get("Score", 0.0)
        maxtopics = [topic for topic in alltopics if topic.get("Score", -1.0) >= maxscore]
        maxdomains = [topic.get("Domain", "") for topic in maxtopics ]
        if len(maxtopics) > 1:
            for topic in maxtopics:
                topic["RobotAsk"] = 1 
                topic["Slots"]["Suggestion"] = robotasksuggestion(maxdomains, 2) 

    if (not alltopics) or (len(alltopics) == 1 and alltopics[0].get("Cnonsense", 0)):
        if usefulcontexts and usefulcontexts[0] and not alltopics:
            alltopics.append(usefulcontexts[0][0])
        #query修正
        alltopics[0]["Query"] = query
        alltopics[0]["Slots"]["Suggestion"] = u"好的。您继续。"



def robotasksuggestion(domains, num):
    sel_domains = domains[:num]#random.sample(domains, num)
    str1 = u"您要选择"
    join_str = u"，还是"
    return join_str.join(sel_domains)
