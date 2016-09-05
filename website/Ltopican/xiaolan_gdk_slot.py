#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: xiaolan_gdk_slot.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-09-01 10:24:14
#########################################################################
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import os
import jieba.posseg as pseg

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
#XiaoLan Slot抽取基础类
class XiaoLanGdkSlot(object):
    """ 
        xiaoi slots抽取公共函数集。
    """
    def __init__(self):
        """
            初始化函数。
        """
        #文本分割正则
        self.punctuationStr = [ur'(?:。|？|！|，|；|\?|\!|,|;)']
        self.searchStr = [ur'(?:检索|搜索|搜询|搜寻|搜个|搜搜|搜一下|搜一些|搜一搜|查查|查询|查寻|查阅|查个|查一下|查一些|查一查|百度一下|百度搜|百度查|谷歌一下|谷歌搜|谷歌查|google)(下|一下|1下){0,1}', ur'(?:^(?:搜|查))(下|一下){0,1}']
        self.searchSplitPattern = re.compile('|'.join(self.punctuationStr + self.searchStr))
        self.timeStr = [ur'(?:\d{1,2}(?::|：)\d{1,2})|(?:(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿|半|两|个|\.){1,4}(?:\.|点|小时|时|分钟|分|秒钟|秒|刻钟|刻))']
        self.remindStr = [ur'(?:提醒|闹钟|闹表|表|通知|告知|叫我|我要|我想|我打算|我准备|我会|我计划|记得)',ur'(?:(?:设|设置|定|整个).{0,4}(?:闹钟|闹表|表))']
        self.remindSplitPattern = re.compile('|'.join(self.timeStr + self.punctuationStr + self.remindStr))
        #停用词过滤词典
        self.punctuation = [u'。',u'？',u'！',u'，',u'；',u'?',u'!',u',',u';']
        self.searchStopWord = [u'阿',u'啊',u'啦',u'唉',u'呢',u'吧',u'了',u'哇',u'呀',u'吗',u'哦',u'哈',u'哟',u'么']
        self.remindStopWord = [u'前',u'后',u'帮',u'能',u'能不能',u'可以',u'我',u'你',u'他',u'她',u'它',u'阿',u'啊',u'啦',u'唉',u'呢',u'吧',u'了',u'哇',u'呀',u'吗',u'哦',u'哈',u'哟',u'么',u'的',u'时候',u'个']
        self.searchFilterWord = set(self.punctuation + self.searchStopWord)
        self.remindFilterWord = set(self.punctuation + self.remindStopWord)

    def checkInput(self,queryobj):
        """
            校验输入参数。
        """
        if type(queryobj) is not unicode:
            query = queryobj.rawtext.strip()
        else:
            query = queryobj.strip()
        return query

    def main(self,query,mode):
        """
            判断待取的字串片段。
        """
        if mode == 'SearchKeyText':
            splitPattern = self.searchSplitPattern
            filterWord = self.searchFilterWord
        elif mode == 'RemindKeyText':
            splitPattern = self.remindSplitPattern
            filterWord = self.remindFilterWord
        res = {}
        text = []
        #print "Query", query
        splitList = re.split(splitPattern,query)
        for part in splitList:
            #print part
            if not part:
                continue
            words =pseg.cut(part)
            wordList = []
            posFlag = False
            wordFlag = False
            for w in words:
                if (not posFlag) and (w.flag.startswith('n') or w.flag.startswith('v')):
                    posFlag = True
                if (not wordFlag) and (not w.word in filterWord):
                    wordFlag = True
                if re.search("\w{2,4}", w.word):
                    posFlag = True
                if wordFlag:
                    wordList.append(w.word)
            if posFlag:
                for i in range(len(wordList)):
                    if wordList[len(wordList) -1 -i] in filterWord and wordList[len(wordList) -1 -i] != u'的':
                        wordList.pop()
                    else:
                        break
                if len(''.join(wordList)) < 2:
                    continue
                text.append(''.join(wordList))       

        if mode == 'SearchKeyText' and text:
            text = text[-1]

        if text:
            res[mode] = ''.join(text)
            return res
        else:
            return None


xiaoLanGdkSlotobj = XiaoLanGdkSlot()
def Slotsearchfind(queryobj):
    """
        抽取检索信息。
    """
    res = {}
    query = xiaoLanGdkSlotobj.checkInput(queryobj)
    return xiaoLanGdkSlotobj.main(query,'SearchKeyText')
    
def Slotremindfind(queryobj):
    """
        抽取提醒信息。
    """
    query = xiaoLanGdkSlotobj.checkInput(queryobj)
    return xiaoLanGdkSlotobj.main(query,'RemindKeyText')


#if __name__=="__main__":
#    for line in sys.stdin:
#        line = line.strip().decode('utf-8')
#        print Slotsearchfind(line)
#        print Slotremindfind(line)
#    print "new file"

