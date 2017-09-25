import induce
import calc1

data='''\
1.2 / ( 11+3)
11 * 10
1 + 1 / 10
2 - 4\
'''

with induce.Tracer():
    for l in data.split('\n'):
        print(l)
        calc1.calc(l)
