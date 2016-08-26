#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topicquestion.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-15 14:47:35
#########################################################################
import re

class topicquestion:
    def __init__(self):
        self.choosere = u"(还是|或是)"
        self.choosesplitre = u"(还是|或是|,|，|、)"
        self.rankidre = u"(最后(?:第)?|倒数(?:第)?|第)(.*?)个"

        self.nore = u"(不|(等|过)会儿|(等|过).*?下|马上|一会)"
        self.yesre = u"(好|可以|行|没问题|嗯|恩)"
        self.common_used_numerals = {u'〇':0, u'O':0, u'零':0, u'那一':1, u"那":1, \
                u'一':1, u'二':2, u'三':3, u'四':4, u'五':5, u'六':6, u'七':7, u'八':8, u'九':9, u'十':10,\
                u'十一':11, u'十二':12, u'十三':13, u'十四':14, u'十五':15, u'十六':16, u'十七':17, u'十八':18, u'十九':19, u'二十':20,\
                u'一十一':11, u'一十二':12, u'一十三':13, u'一十四':14, u'一十五':15, u'一十六':16, u'一十七':17, u'一十八':18, u'一十九':19,
                }
        pass

    def question(self, answer, issue):
        if re.search(self.choosere, issue):
            #选择句
            choosenum = self.choosefuc(answer, issue)
            if choosenum:
                return {"ChooseNum": choosenum}
            else:
                return None
        else:
            yesorno = self.yesnofuc(answer, issue)
            if yesorno:
                return {"YesorNo": yesorno}
            else:
                return None

    def yesnofuc(self, answer, issue):
        if re.search(self.nore, answer):
            return "no"
        elif re.search(self.yesre, answer) or len(answer) <= 3:
            return "yes"
        return None

    def setintersect(self, t1, t2):
        t1 = set(t1)
        t2 = set(t2)
        return len(t1&t2)

    def choosefuc(self, answer, issue):
        issue = re.sub(" ", "", issue)
        issues = re.sub(self.choosesplitre, " ", issue).split()

        badpos = -1

        #判断用户说话方式
        matchobj = re.search(self.rankidre, answer)
        if matchobj:
            ranksort = matchobj.groups()[0]
            ranknum = matchobj.groups()[1]
            if u"最后" in ranksort or u"倒数" in ranksort:
                rankpos = -1
            else:
                rankpos = 0
            ranknum = self.common_used_numerals.get(ranknum, badpos)
            if ranknum < 0:
                return  badpos
            if rankpos == 0 :
                return ranknum
            if rankpos < 0:
                return len(issues) - ranknum + 1


        else:            
            #不是第几个
            issues_score = [self.setintersect(t, answer) for t in issues]
            if sum(issues_score) == 0.0:
                return badpos
            return 1 + issues_score.index(max(issues_score))

    def main(self, answer, issue):
        result = self.question(answer, issue)
        if result:
            return [{
                    "Domain" : "Q&A",
                    "Score" : 1.0,
                    "Slots" : result,
                    "Intent": "Ask"
                    }]
        else:
            return []




if __name__=="__main__":
    obj = topicquestion()
    print obj.main(u"撸串吧", u"你是要啤酒、烤串、还是什么")

