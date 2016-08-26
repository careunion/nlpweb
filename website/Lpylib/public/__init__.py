#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: topic_judge.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2016-04-20 11:13:28
#########################################################################
import re
import math
import os
from editdis import *
from numberfind import *

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

class Tools:
    def __init__(self):
        self.ed = Editdis().mined
        self.number = NumberFind().numberfind
        

if __name__=="__main__":
    _obj = Tools()
    print _obj.ed(u"我不舒服", u"我很不舒服")
    print _obj.number("我刚才3点钟测得四十五吧")

