#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: Lsimtext.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-07-12 20:45:01
#########################################################################

import Lpylib.public as public

tool_obj = public.Tools()

def topn_simtexts_get(req_obj, requsers_obj = None):
    query = req_obj.Raw_text
    textinfo_list = []
    
    #必须要求WordSet里面有Text，然后用去跟query比较，计算分数
    #但是需求方很变态，说Text也想弄成多个字符串#拼接在一起的，所以给做了
    for _textdict in req_obj.Word_set:
        _texts = _textdict.get("Text", "").split("#")
        sims = []
        for _text in _texts:
            sims.append( tool_obj.ed(query, _text) )
        biggestsim = max(sims)
        if biggestsim > 0.0:
            _textdict["Score"] = biggestsim
            textinfo_list.append(_textdict)


    #sortedlist = sorted(sim_dict.items(), key=lambda x:x[1], reverse=True)[:req_obj.Simtext_topn]
    sortedlist = sorted(textinfo_list, key=lambda x:x.get("Score", 0.0), reverse=True)[:req_obj.Simtext_topn]
    #print sortedlist[0][0], sortedlist[0][1]
    return sortedlist

