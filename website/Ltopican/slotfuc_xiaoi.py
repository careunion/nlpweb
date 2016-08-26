#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: slotfuc_xiaoi.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-23 14:55:01
#########################################################################
import re

#发现用户是否想询问优惠券相关的东西
def Slotcouponfind(queryobj):
    query = queryobj.rawtext
    coupon_has_tag = False
    if re.search(u"(优惠券|优惠|现金券|体验券|礼品券|折扣券|特价券|换购券|通用券|贵宾券|抵扣券|领券|有什么券)", query):
        coupon_has_tag = True
    if coupon_has_tag:
        return {"Coupon" : coupon_has_tag}
    else:
        return None


if __name__=="__main__":
    print "new file"

