#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: models.py
# Author: yaojia
# mail: yaojia@brandbigdata.com
# Created Time: 2015-11-17 13:04:29
#########################################################################

from django.db import models
from django import forms
from django.forms import ModelForm
# Create your models here.


class Contexts(models.Model):
    uid = models.CharField(max_length=100)
    query = models.TextField()
    context = models.TextField()
    
    def __unicode__(self):
        return self.uid

