#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: test.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-09 11:32:49
#########################################################################
import urllib
import urllib2
import json
import time
import sys

for line in sys.stdin:
    
    line = line.strip()
    if not line:continue
    s = time.time()
    test_data = {"Appid":"xiaoi","Skey":"xiaoi436dg","Uid":"yjte5k0",
    "Raw_text":line,
    #"Robot_question":"你要选长春吗",
    "Topic_topn":10,"Simtext_topn":2,\
            "Word_set":[
                {"Text":"我想去吃饭了#吃饭了#去吃饭吧", "Textid":"435436"},
                {"Text":"我不去吃饭了", "Textid":"135436"},
                ],
            "Context_text":[],"Context_topic":[],"Version":"","Fuc_id":""}
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0'}
    body = json.dumps(test_data)
    
    requrl = "http://120.76.158.123:8006/api/"
    post_body=body#urllib.urlencode(body)
    req=urllib2.Request(requrl, headers=headers, data=post_body)
    res=urllib2.urlopen(req)
    t = res.read()
    t = json.loads(t )
    print "---------------", line#.encode("utf-8")
    print json.dumps(t, ensure_ascii=False)
    
    e = time.time()
