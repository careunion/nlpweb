#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from models import *
from django.views.decorators.csrf import csrf_exempt
import os,sys
import json
import re
import time
import urllib
import urllib2
import random
import Lpylib
import Lreq
import Ltopic
import Lsimtext
import Lresp
import Lpylib.topic.sen_judge as sen_judge
import logging



reload(sys)
sys.setdefaultencoding( "utf-8" )
logger = logging.getLogger("django")

#获取基础用户信息等
logger.debug("Loading Username")
appusers_obj = Lreq.Appusers("appuser.txt")
requsers_obj = Lreq.Requsers()

#句子正确性判断
logger.debug("Loading Class")
sen_obj = sen_judge.SenJudge()

@csrf_exempt
def api(req):
    if True:
        #获取基本的数据信息
        if req.method == "POST":
            query = req.body
        elif req.method == "GET":
            query = req.body
        query_json = json.loads(query)
        
        #获取request基本信息
        req_obj = Lreq.Lreq(query_json)
        logger.debug(req_obj.pprint(logger))
        #身份验证
        if not appusers_obj.certif(req_obj):
            logger.debug("平台信息错误")
            return HttpResponse(BadResp(1, req_obj) , content_type="application/json")
        #query验证
        if sen_obj.sen_judge_main(req_obj.Raw_text) > 0.9:
            logger.debug("Query 验证失败")
            return HttpResponse(BadResp(101, req_obj) , content_type="application/json")

        #topics 获取, 即使无topic，也会返回一个空的list
        topn_topics = Ltopic.topn_topics_get(req_obj, requsers_obj) 
        #requsers_obj.pprint(req_obj)

        #sim_text 获取
        topn_simtexts = Lsimtext.topn_simtexts_get(req_obj, requsers_obj)

        #context信息更新，不过只有在有具体topic情况下，才更新用户个人context
        if topn_topics:
            req_obj.append(topn_topics[0])
            requsers_obj.append(req_obj)
        
        requsers_obj.save()

        logger.debug("topn_topics:" + json.dumps(topn_topics, ensure_ascii=False))
        logger.debug("topn_simtexts:" + json.dumps(topn_simtexts, ensure_ascii=False))
        return HttpResponse(GoodResp(req_obj, topn_topics, topn_simtexts), content_type="application/json")
    else:
        return HttpResponse(BadResp(-1) , content_type="application/json")

def BadResp(err_type, req_obj = None):
    return json.dumps(Lresp.Lresp(err_type, req_obj).resp)

def GoodResp(req_obj, topics, simtexts):
    return json.dumps(Lresp.Lresp(0, req_obj, topics, simtexts).resp)

