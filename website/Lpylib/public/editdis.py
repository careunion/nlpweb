#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: ed.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2016-04-14 22:38:45
#########################################################################
import re
import sys

class Editdis:
    def sametextpre(self, s1, s2):
        all_has_num =  len(set(s1) & set(s2))
        return 2.0 * all_has_num / (len(s1) + len(s2))
    
    def mined(self, s1, s2):
        if s1 == s2:
            return 1.0
        s1 = re.sub(u"(\s|，|,|。|的|说|和|着|我|这|你|很|是|都|也|就|人|呢|可以)", "", s1)
        s2 = re.sub(u"(\s|，|,|。|的|说|和|着|我|这|你|很|是|都|也|就|人|呢|可以)", "", s2)
        badcostwords = set([u"不", u"没"])
        badcost = 5 
        m, n = len(s1), len(s2)
        colsize, matrix = m + 1, []
        for i in range((m + 1) * (n + 1)):
            matrix.append(0)
        #s1
        cost = 0
        for i in range(colsize):
            matrix[i] = cost
            if i == m:continue
            if s1[i] in badcostwords:
                cost += badcost
            else:
                cost += 1
        #s2
        cost = 0
        for i in range(n + 1):
            matrix[i * colsize] = cost
            if i == n:continue
            if s2[i] in badcostwords:
                cost += badcost
            else:
                cost += 1
        #s1-s2
        for i in range(n + 1)[1:n + 1]:
            for j in range(m + 1)[1:m + 1]:
                cost = 0
                if s1[j - 1] == s2[i - 1]:
                    cost = 0
                elif s1[j - 1] in badcostwords or s2[i - 1] in badcostwords:
                    cost = badcost
                else:
                    cost = 1
    
    
                if s1[j - 1] in badcostwords:
                    s1cost = badcost
                else:
                    s1cost = 1
                if s2[i - 1] in badcostwords:
                    s2cost = badcost
                else:
                    s2cost = 1
    
                minValue = matrix[(i - 1) * colsize + j] + s2cost
                if minValue > matrix[i * colsize + j - 1] + s1cost:
                    minValue = matrix[i * colsize + j - 1] + s1cost
    
                if minValue > matrix[(i - 1) * colsize + j - 1] + cost:
                    minValue = matrix[(i - 1) * colsize + j - 1] + cost
                matrix[i * colsize + j] = minValue
        ed_dis = matrix[n * colsize + m] * 1.0 / max([m, n, 1])
        ed_dis = max(-1,  1 - ed_dis) / 1.0
        same_dis = self.sametextpre(s1, s2)
        all_dis = max(0, (ed_dis + same_dis)/2)
        return all_dis


