""" Helper module """
import sys

def slurp(src):
    """
    read a file completely
    """
    with open(src) as myfile:
        return myfile.read()

def slurpl(src):
    """
    read a file completely, and split lines
    """
    return slurp(src).split('\n')

def slurplstrip(src):
    """
    read a file completely, and split lines and strip them
    """
    return [line.strip() for line in slurpl(src)]


def slurparg():
    """ use first argument """
    return slurp(sys.argv[1])

def slurplarg():
    """ use first argument """
    return slurpl(sys.argv[1])

def slurplstriparg():
    """ use first argument """
    return slurplstrip(sys.argv[1])
