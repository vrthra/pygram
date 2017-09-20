# -*- coding: utf8 -*-
import dateparser

data='''\
12/12/12
Fri, 12 Dec 2014 10:55:50
Martes 21 de Octubre de 2014
Le 11 Décembre 2014 à 09:00
13 января 2015 г. в 13:34
1 เดือนตุลาคม 2005, 1:00 AM
2015, Ago 15, 1:08 pm
22 Décembre 2010
1 hour ago
Il ya 2 heures
1 anno 2 mesi
yaklaşık 23 saat önce
Hace una semana
2小时前
02-03-2016
le 02-03-2016
18-12-15 06:00
January 12, 2012 10:00 PM EST
January 12, 2012 10:00 PM -0500
January 12, 2012 10:00 PM
January 12, 2012 10:00 PM
January 12, 2012 10:00 PM
10:00 am
10:00 am EST
now EST
2 minutes ago
4 minutes ago
10:40 pm PKT
20 mins ago EST
December 2015
December 2015
December 2015
March
March
August
December 2015\
'''

import induce
lines = data.split('\n')
for l in lines:
    print l
    with induce.Tracer(l):
        dt = dateparser.parse(l)
