#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: urls.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2015-11-17 11:34:49
#########################################################################

from django.conf.urls import patterns, url

from polls import views

urlpatterns = patterns('',
     (r'^yisi', 'polls.views.yisi'),
    )
