#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: Lresp.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-07-13 14:39:02
#########################################################################
import Lreq

class Lresp:
    def __init__(self, err_type, Lreqobj = None, topics = [], simtexts = []):
        self.resp = {}
        if not Lreqobj:
            Lreqobj = Lreq.Lreq()

        self.resp["Version"] = Lreqobj.Version
        self.resp["Status"] = 1
        self.resp["Msgcode"] = self.msg_gen(err_type)
        #错误代码，只有0，代表正确返回
        self.resp["Errcode"] = err_type
        self.resp["Result"] = {}

        #脏句子
        if err_type ==  101:
            self.resp["Result"]["Status"] = 2
        elif topics or simtexts:
            self.resp["Result"]["Status"] = 1
        
        #相似文本
        if simtexts:
            self.resp["Result"]["Simtexts"] = simtexts
            #for sim_text, score in simtexts:
            #    _dict = {}
            #    _dict["Text"] = sim_text
            #    _dict["Score"] = score
            #    self.resp["Result"]["Simtexts"].append(_dict)
        if topics:
            self.resp["Result"]["Topics"] = []
            for topic_dict in topics:
                self.resp["Result"]["Topics"].append(topic_dict)

    def msg_gen(self, err_type):
        if err_type == -1:
            return "请求数据结构"
        if err_type == 0:
            return "success"
        if err_type == 1:
            return "身份验证不通过"
        if err_type == 101:
            return "Raw_text为脏句子"

                

