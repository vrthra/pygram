import arith
import induce

# sample expressions posted on comp.lang.python, asking for advice
# in safely evaluating them
rules= '''\
( A - B ) == 0
(A + B + C + D + E + F + G + H + I) == J
(A + B + C + D + E + F + G + H) == I
(A + B + C + D + E + F) == G
(A + B + C + D + E) == (F + G + H + I + J)
(A + B + C + D + E) == (F + G + H + I)
(A + B + C + D + E) == F
(A + B + C + D) == (E + F + G + H)
(A + B + C) == (D + E + F)
(A + B) == (C + D + E + F)
(A + B) == (C + D)
(A + B) == (C - D + E - F - G + H + I + J)
(A + B) == C
(A + B) == 0
(A+B+C+D+E) == (F+G+H+I+J)
(A+B+C+D) == (E+F+G+H)
(A+B+C+D)==(E+F+G+H)
(A+B+C)==(D+E+F)
(A+B)==(C+D)
(A+B)==C
(A-B)==C
(A/(B+C))
(B/(C+D))
(G + H) == I
-0.99 <= ((A+B+C)-(D+E+F+G)) <= 0.99
-0.99 <= (A-(B+C)) <= 0.99
-1000.00 <= A <= 0.00
-5000.00 <= A <= 0.00
A < B
A < 7000
A == -(B)
A == C
A == 0
A > 0
A > 0.00
A > 7.00
A <= B
A < -1000.00
A < -5000
A < 0
A==(B+C+D)
A==B
I == (G + H)
0.00 <= A <= 4.00
4.00 < A <= 7.00
0.00 <= A <= 4.00 <= E > D
123E0 > 1000E-1 > 99.0987
123E+0
1000E-1
99.0987
abc
20 % 3
14 // 3
12e2 // 3.7\
'''.split('\n')

myvars={'A': 0, 'B': 1.1, 'C': 2.2, 'D': 3.3, 'E': 4.4, 'F': 5.5, 'G':
       6.6, 'H':7.7, 'I':8.8, 'J':9.9, "abc": 20}

# define tests from given rules
tests = [(t, eval(t,myvars)) for t in rules]
# copy myvars to EvalConstant lookup dict
arith = arith.Arith(myvars)
for test,expected in tests:
    with induce.Tracer(test):
        result = arith.eval( test )
        print test,expected,"<>",result
