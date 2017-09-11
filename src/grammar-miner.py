#!/usr/bin/env python
import sys
import tracer
import grammar
from urlparse import urlparse

def slurp(src):
    with open(src) as x: return x.readlines()

if __name__ == "__main__":
    lines = [l.strip() for l in slurp(sys.argv[1])]
    # Infer grammar
    mygrammar = grammar.Grammar(urlparse, lines)

    # Output it
    print("Merged grammar ->\n%s" % mygrammar)
