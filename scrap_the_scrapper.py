#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import  time
import sys
from html import unescape

import re

class ScrapTheScrapper(object):
  finished = False
  FILES = "dolnoslaskie.html   kujawsko_pomorskie.html  lodzkie.html  lubelskie.html  lubuskie.html  malopolskie.html  mazowieckie.html  opolskie.html  podkarpackie.html  podlaskie.html  pomorskie.html  slaskie.html  swietokrzyskie.html  warminsko_mazurskie.html  wielkopolskie.html  zachodniopomorskie.html"
  def __init__(self,):
    print("ok")
    self.files = self.FILES.split("  ")
    self.loop()

  def sync(self):
    os.system("git pull -ff https://github.com/szczepienia/szczepienia.github.io.git")
    print("sync ok")

  def load(self,):
    out = ""
    filter = "<table>"
    for f in self.files:
     htm = '\n'.join(open(f.strip()).readlines()[5:])
     out+=htm
    open('all.html','w').write(out)
    terminy = re.finditer(r'(?P<header><tr\s.*?data-search-vaccines="(?P<vaccine>.*?)".*?>)(?P<body>.*?)(</tr>)', out, re.MULTILINE|re.DOTALL)
    for t in terminy:
      if t.group('vaccine')=="Moderna":
         if t.group(0).find("Pfizer")>-1:
           print("WTF?: %s" % (t.group(0)))
         #print("Moderna hit")
         filter += t.group("header")
         for m in re.finditer(r'(?P<Miasto><td>(?P<town>.*?)</td>)\s+'+
                               '(?P<Data><td data-order.*?>(?P<data>(?P<dzien>\d+)&nbsp;(?P<miesiac>(czerwca))).*?</td>)\s+'+
                               '(?P<Godz><td\s+class=".*?times.*?".*?>.*?</td>)\s+'+
                               '(?P<Rodzaj><td.*?>.*?Moderna.*?</td>)\s+'+
                               '(?P<Adres><td.*?>.*?</td>)\s+'+
                               '(?P<Umow><td.*?>.*?</td>)'+
                               #'<div class="extended-times">'
                               '', t.group('body'), re.MULTILINE|re.DOTALL):
           if (m.group('miesiac')=='czerwca' and int(m.group('dzien')) in range(13,15)):
             filter+=m.group(0)
             #Kolumna Godz
             slots = re.finditer(r'<td\s+class=".*?times.*?".*?>(?P<ss>'+
                                '(?:<div class="slot-count">\(terminów: <strong>(?P<term_cnt>\d+)</strong>\)</div>.*?<div class="extended-times">(?P<multi2>.*?)</div>)|'+
                                '(?P<multi>(?:\d+:\d\d)(?:<br/>\d+:\d\d)+)|'+
                                '(?P<single>(?:\d+:\d\d)))'+
                             '.*?</td>', m.group('Godz'), re.MULTILINE|re.DOTALL)
             #print(slots)
             for slot in slots:
               if slot is None:
                 #slot = re.match(r'<td\s+class=".*?times.*?".*?>(?:<div class="slot-count"></div>)'+
                 #             '.*?</td>', m.group('Godz'), re.MULTILINE|re.DOTALL)
                 print("ERROR: Nie matchuje godz zawartosc: %s" % m.group('Godz'))
               #print(slot)
               ext_terms = slot.group('term_cnt')
               multi = slot.group('multi')
               single = slot.group('single')
               if ext_terms:
                 terminow = "%s terminów:" % (ext_terms)
                 multi = slot.group('multi2').strip()
               if multi:
                 terminow = "terminy: %r" % (','.join(multi.split("<br/>")))
               else:
                 terminow = "1 termin: " + single
             
             #Kolumna adres
             adr_m = re.match(r'<td.*?>.*?'+
                              '.*?href="(?P<maplink>.*?google.com/maps.*?)"'
                              '.*?<div class="point-description">(?P<point>.*?)</div>'+
                              '<div class="point-address">(?P<pointa>.*?)</div>'+
                              '.*?</td>',m.group('Adres'),re.MULTILINE|re.DOTALL)
             adr_str =  "%s, %s" % (adr_m.group('point'), adr_m.group('pointa'))
             #print(adr_m)
             #<div class="point-description">   
          
             #Kolumna umów
             umow_m = re.match(r'<td.*?>.*?'+
                               '<a href="tel:(?P<tel>\+?\d+)" title="Zadzwoń do punktu'+
                               '.*?</td>', m.group('Umow'), re.MULTILINE|re.DOTALL)
             umow_str="📞: %s" % (umow_m.group(1))
             print("%s Moderna, %s, %s, %s, %s" % (unescape(m.group('data')), m.group('town'), terminow, adr_str, umow_str) ) 
         filter += "</tr>"
    filter += "</table>"      
    open('filtered.html','w').write(filter)

  def loop(self):
    while True:
      if self.finished:
        break
      self.sync()
      self.load()
      if self.finished:
        break
      time.sleep(5)


  def wait_for_exit(self, ):
    print("wait for exit")
    while self.finished is False :
     time.sleep(1)
     print("not finished")

s = ScrapTheScrapper()
#s.wait_for_exit()
