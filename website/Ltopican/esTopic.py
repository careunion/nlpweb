#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: esTopic.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-15 13:46:29
#########################################################################
import urllib2
import json
import sys
import os
#import jieba


pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

class esTopic(object):
    """
        Slots插槽函数类，为其提供es检索相关功能。
    """
    def __init__(self, url="120.76.219.105:9200"):
        self.Website = url
        self.Stopword = set([])
        self.Extendword = []
        self.dictload()

    def dictload(self):
        f = open(pwd_path + '/data/stopword.dict','r')
        for line in f:
            line = line.strip()
            if line:
                self.Stopword.add(line.decode('utf-8'))
        f.close()

        f = open(pwd_path + '/data/extendword20160816.dict','r')
        for line in f: 
            line = line.strip()
            if line:
                wordlist = line.decode('utf-8').split(' ')
                #print json.dumps(wordlist,ensure_ascii = False)
                if len(wordlist) > 1:
                    self.Extendword.append([set(wordlist),wordlist])
        f.close()

    #一个query在多个fields下的查询，且fields的权重不一样
    def multifiledsearch(self, dataindex, datatype, size, query, fieldinfos = None):
        #fieldinfos:[[filed, score], [field, score],,,, ]
        #fieldinfos如果不传入，则直接表示_all，且fields的权重都为1
        esmatchs = []
        esquery = {
                "query":{
                    "bool":{
                        "should": esmatchs
                    }
                },
                "size" : size
            }
        if not fieldinfos:
            esmatchs.append(self.matchfiledgen("_all", query))
        else:
            for field, boostscore in fieldinfos:
                esmatchs.append(self.matchfiledgen(field, query, boostscore))
        requrl = "http://%s/%s/%s/_search" %(self.Website, dataindex, datatype)
        return self.esquerysearch(requrl, esquery) 

    def matchfiledgen(self, field, query, boostscore = 1.0):
        esmatch = {
                "match": {
                    field: {
                        "query": query,
                        "boost": boostscore
                }}}
        return esmatch

    #单一域的全匹配功能，如果不指定，就是直接_all
    def singlefieldsamesearch(self, dataindex, datatype, size, query, field="_all"):
        searchstr = "%s:\"%s\"" %(field, query)
        esquery = {
                "query":{
                    "query_string":{
                        "query": searchstr
                        }
                    },
                "size":size
                }
        requrl = "http://%s/%s/%s/_search" %(self.Website, dataindex, datatype)
        return self.esquerysearch(requrl, esquery)

    #根据url，query对象，进行search
    def esquerysearch(self, requrl, esquery):
        #print json.dumps(esquery, ensure_ascii=False) 
        body = json.dumps(esquery)
        req = urllib2.Request(requrl, data=body)
        res = urllib2.urlopen(req)
        return json.loads(res.read())

    def esupload(self, dataindex, datatype, datainfo):
        requrl = "http://%s/%s/%s/" %(self.Website, dataindex, datatype)
        self.esquerysearch(requrl, datainfo)

    #返回格式归一化
    def datareg(self, resultjson):
        results = resultjson["hits"]["hits"]
        for result in results:
            print result["_score"], result["_source"]["title"], result["_source"]["content"]
        print "\n\n\n"
        for result in results:
            print result["_score"], result["_source"]["title"]

    def queryExtend(self,queryobj):
        """
            query扩展支持。
        """
        filterlist = []
        query = queryobj.segtext
        #query = list(jieba.cut(queryobj))
        for word in query:
            if word in self.Stopword:
                continue
            else:
                filterlist.append(word)
        resset = set(filterlist)
        extendset = set([]) 
        for word in resset:
            for line in self.Extendword:
                if word in line[0]:
                    count = 0
                    for extend in line[1]:
                        if (not extend in resset) and (not extend in extendset):
                            extendset.add(extend)
                            count = count + 1
                        if count > 1:
                            break
                    break
        res = ' '.join(filterlist).replace(u"操", "")
        if extendset:
            res = res + ' ' + ' '.join(extendset)
        print "query extend：", queryobj.rawtext, "->", res
        return res
        

    def resRerank(self,resultjson,fields):
        """
            检索结果重排。
        """
        res = []
        results = resultjson["hits"]["hits"]
        for result in results:
            temp = {}
            temp["Score"] = min(result["_score"], 1.0)
            for field in fields:
                if result["_source"][field]:
                    temp[field] = result["_source"][field]
                else:
                    temp[field] = ''
            res.append(temp)
            
        return res

if __name__=="__main__":
    obj = esTopic()
    for line in sys.stdin:
        line = line.strip()
        print obj.queryExtend(line)
        #t = obj.multifiledsearch("xiaolan", "sportlist0815v2", 5, line, [["content", 2],["title", 1]])
        #print json.dumps(obj.resRerank(t,["content","title"]),ensure_ascii = False)
