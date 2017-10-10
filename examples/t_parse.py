import induce
import collections

def lexical_split(mystr):
    ltoks = mystr.split()
    return ltoks

def basic_parse(line):
    astr = line.replace(',','')
    astr = astr.replace('and','')
    tokens = lexical_split(astr)
    dept = None
    number = None
    result = []
    option = []
    for tok in tokens:
        if tok == 'or':
            result.append(option)
            option = []
            continue
        if tok.isalpha():
            dept = tok
            number = None
        else:
            number = tok
        if dept and number:
            option.append((dept,number))
    else:
        if option:
            result.append(option)
    return result

for line in induce.helpers.slurplarg():
    if not line.strip(): continue
    with induce.Tracer(line):
       parts = basic_parse(line)
