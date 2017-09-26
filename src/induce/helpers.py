import sys

def slurp(src):
    with open(src) as x: return x.read()

def slurpl(src):
    with open(src) as x: return x.readlines()

def slurplstrip(src):
    with open(src) as x: return [l.strip() for l in x.readlines()]


def slurparg():
    return slurp(sys.argv[1])

def slurplarg():
    return slurpl(sys.argv[1])

def slurplstriparg():
    return slurplstrip(sys.argv[1])
