import induce
import collections

def basic_parse(astr):
    astr=astr.replace(',','')
    astr=astr.replace('and','')
    tokens=astr.split()
    dept=None
    number=None
    result=[]
    option=[]
    for tok in tokens:
        if tok=='or':
            result.append(option)
            option=[]
            continue
        if tok.isalpha():
            dept=tok
            number=None
        else:
            number=tok
        if dept and number:
            option.append((dept,number))
    else:
        if option:
            result.append(option)
    return result

for line in induce.helpers.slurplarg():
    with induce.Tracer(line):
       parts = basic_parse(line)
