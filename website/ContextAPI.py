#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: test.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-08 12:03:01
#########################################################################
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from polls.models import Contexts
import json
from django.core.exceptions import ObjectDoesNotExist

class Context(object):
    """
        上下文数据库访问接口。
    """
    def __init__(self):
        pass

    def loadData(self):
        """
            从数据库加载数据到内存。
        """
        contextList = Contexts.objects.all()
        contextDict = {}
        for line in contextList:
            contextDict[line.uid] = [json.loads(line.query),json.loads(line.context),False]
        return contextDict

    def dumpData(self,contextDict):
        """
            内存数据有更新时，保存数据到数据库。
        """
        for key,value in contextDict.items():
            if value[2]:
                query = json.dumps(value[0],ensure_ascii = False)
                context = json.dumps(value[1],ensure_ascii = False)
                try:
                    p = Contexts.objects.get(uid=key)
                except ObjectDoesNotExist:
                    p = Contexts.objects.create(uid=key)
                p.query = query
                p.context = context
                p.save()



if __name__=="__main__":
    a = {'1':[['12'],['13'],True],'2':[['22'],['23'],True]}
    obj = Context()
    obj.dumpData(a)
    #print obj.loadData()
