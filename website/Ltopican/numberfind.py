#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: number.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2015-09-09 20:39:49
#########################################################################
import re
import sys
import os
pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

common_used_numerals = {'〇':0, 'O':0, '零':0, \
        '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, \
        '百':100, '千':1000, '万':10000, '亿':100000000, \
        '两':2, '壹':1, '贰':2, '叁':3, '肆':4, '伍':5, '陆':6, '柒':7, '扒':8, '玖':9, '拾':10, '佰':100, '仟':1000, \
        '仟万':10000000, '千万':10000000, '百万':1000000, '佰万':1000000, '十万':100000, '拾万':100000 \
        }

class NumberFind:
    def numbertrans(self, numcn):
        split_cns = ["亿", "千万", "仟万", "百万", "佰万", "十万", "拾万", "万", "千", "仟", "佰", "百", "十", "拾"]
    
        if numcn.isdigit():
            #如果是数字，直接转为数字
            return int(numcn)
    
        #从最大的单位开始分割，然后 upper * 最大单位 + lower, 然后 upper 跟 lower 各自递归撒
        #如         二亿零四十万  ==   二 * 亿       + 零四十万
        for cn_num in split_cns:
            nums = numcn.split(cn_num)
            if len(nums) > 1:
                upper = self.numbertrans(nums[0])
                lower = self.numbertrans(nums[1])
                if upper == 0:
                    upper = 1
                return upper * common_used_numerals[cn_num] + lower
                
        numcn_len = len(numcn)
        if numcn_len == 3:
            #刚好是一个字的时候，取字典内的数字
            return common_used_numerals[numcn]
        elif numcn_len > 3:
            #如果是多个字，[0-9]的汉字，直接转成相应的数字
            numcns = [t.encode("utf-8") for t in numcn.decode("utf-8")]
            nums = ""
            for _num in numcns:
                if _num.isdigit():
                    nums += _num
                    continue
                nums += str(common_used_numerals[_num])
            return int(nums)
        elif numcn_len == 0:
            return 0
    def numberfind(self, cn_str):
        numstr = "(?:\d|一|二|三|四|五|六|七|八|九|〇|零|十|百|千|万|亿)"
        numre = re.compile(numstr + "+(?:(?:\.|点)" + numstr + "+){0,1}")
        _obj = re.findall(numre, cn_str)
        if not _obj:
            return []
       
        num_list = []
        for num_cn in _obj:
            num_cns = re.split("(?:点|\.)", num_cn)
            if len(num_cns) == 1:
                pre_num = self.numbertrans(num_cns[0])
                num_list.append( str(pre_num)  )
            elif len(num_cns) == 2:
                pre_num = self.numbertrans(num_cns[0])
                aft_num = self.numbertrans(num_cns[1])
                num_list.append( str(pre_num) + "." + str(aft_num) )
        return num_list

