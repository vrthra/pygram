import arith
import induce

# sample expressions posted on comp.lang.python, asking for advice
# in safely evaluating them
rules= induce.slurplstriparg()
myvars={'AAAA': 0, 'BBBB': 1.1, 'CCCC': 2.2, 'DDDD': 3.3, 'EEEE': 4.4, 'FFFF': 5.5, 'GGGG': 6.6, 'HHHH':7.7, 'IIII':8.8, 'JJJJ':9.9, "abc": 20, }

# define tests from given rules
tests = [(t, eval(t,myvars)) for t in rules if t.strip() != '']
# copy myvars to EvalConstant lookup dict
arith = arith.Arith(myvars)
for test,expected in tests:
    with induce.Tracer(test):
        result = arith.eval( test )
        print(test,expected,"<>",result)
