# romanNumerals.py
#
# Copyright (c) 2006, Paul McGuire
#

from pyparsing import *

def romanNumeralLiteral(numeralString, value):
    return Literal(numeralString).setParseAction(replaceWith(value))

one         = romanNumeralLiteral("I",1)
four        = romanNumeralLiteral("IV",4)
five        = romanNumeralLiteral("V",5)
nine        = romanNumeralLiteral("IX",9)
ten         = romanNumeralLiteral("X",10)
forty       = romanNumeralLiteral("XL",40)
fifty       = romanNumeralLiteral("L",50)
ninety      = romanNumeralLiteral("XC",90)
onehundred  = romanNumeralLiteral("C",100)
fourhundred = romanNumeralLiteral("CD",400)
fivehundred = romanNumeralLiteral("D",500)
ninehundred = romanNumeralLiteral("CM",900)
onethousand = romanNumeralLiteral("M",1000)

numeral = ( onethousand | ninehundred | fivehundred | fourhundred |
            onehundred | ninety | fifty | forty | ten | nine | five |
            four | one ).leaveWhitespace()

romanNumeral = OneOrMore(numeral).setParseAction( lambda s,l,t : sum(t) )
