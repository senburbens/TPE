# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from py2neo import authenticate, Graph, Node, Relationship
from datetime import datetime
import json
from textblob import TextBlob
import re

# Create your views here.
authenticate("localhost:7474", "neo4j", "newbensur3190")
graph = Graph()


from django.http import HttpResponse


def index(request):
    liste = list()
    contenu = graph.run("MATCH p = (t:Tweet)-->(s:Sentiment)  RETURN t.text, t.latitude, t.longitude, t.date, s.polarite").data()
    for el in contenu :
	liste.append({'text':el['t.text'].replace("'", "\'").encode('utf8'),'latitude':el['t.latitude'].encode('utf8'),'longitude':el['t.longitude'].encode('utf8'), 'date':el['t.date'].encode('utf8'), 'polarite':el['s.polarite'].encode('utf8')})
    #longueurListe = len(liste)
    return render(request, "tpe/index.html", locals())
    
