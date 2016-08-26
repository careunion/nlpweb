#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: IdentWeatherCity.py
# Author: yaojia
# mail: hityaojia@163.com 
# Created Time: 2016-08-17 16:45:53
#########################################################################
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import re
import jieba

pwd_path = data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
	
class IdentWeatherCity(object):
    """
        抽取可查天气城市。
    """
    def __init__(self):
        self.WeatherCitySet = set([])
        self.CitySet = set([])
        self.CountyCityDict = {}
        self.ReplacePattern = re.compile(u"(地区|市|州|区|自治县|县)$")

        self.loadData()

    def loadData(self):
        f = open(pwd_path + '/data/weather_has_city.data','r')
        for line in f:
            self.WeatherCitySet.add(line.strip().decode('utf-8'))
        f.close()
        f = open(pwd_path + '/data/weather_city.data','r')
        for line in f:
            self.CitySet.add(line.strip().decode('utf-8'))
        f.close()
        f = open(pwd_path + '/data/weather_county_city.data','r')
        for line in f:
            elements = line.strip().decode('utf-8').split('\t')
            self.CountyCityDict[elements[0]] = elements[1]
        f.close()

    def getNgram(self,words,n):
        length = len(words)
        if n >= length:
            return [''.join(words)]
        elif n <= 1:
            return words

        res = []
        for i in range(length - n + 1):
            if (i + n) == length:
                res.append(''.join(words[i:]))
            else:
                res.append(''.join(words[i:i+n]))
        return res

    def main(self,query):
        words = list(jieba.cut(query))
        words2gram = self.getNgram(words,2)
        words3gram = self.getNgram(words,3)
        words = words + words2gram + words3gram
        for word in words:
            _word = self.ReplacePattern.sub("",word)
            if len(_word) >= 2:
                word = _word
            if self.CountyCityDict.has_key(word):
                if word in self.WeatherCitySet:
                    return word
                elif self.CountyCityDict[word] in self.WeatherCitySet:
                    return self.CountyCityDict[word]
        for word in words:
            _word = self.ReplacePattern.sub("",word)
            if len(_word) >= 2:
                word = _word
            if (word in self.CitySet) and (word in self.WeatherCitySet):
                return word

        return None



if __name__=="__main__":
    obj = IdentWeatherCity()
    for line in sys.stdin:
        line = line.strip()
        print obj.main(line)

