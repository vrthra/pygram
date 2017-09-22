import induce
import calc1

data='''\
1.2 / ( 11+3)\
'''

for l in data.split('\n'):
    print l
    with induce.Tracer():
        calc1.calc(l)
