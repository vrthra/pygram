import arith
import induce, helpers

with induce.grammar() as g:
    # sample expressions posted on comp.lang.python, asking for advice
    # in safely evaluating them
    rules= helpers.slurplstriparg()
    myvars={'A': 0, 'B': 1.1, 'C': 2.2, 'D': 3.3, 'E': 4.4, 'F': 5.5, 'G':
           6.6, 'H':7.7, 'I':8.8, 'J':9.9, "abc": 20, }

    # define tests from given rules
    tests = [(t, eval(t,myvars)) for t in rules]
    # copy myvars to EvalConstant lookup dict
    arith = arith.Arith(myvars)
    for test,expected in tests:
        with induce.Tracer(test, g):
            result = arith.eval( test )
            print test,expected,"<>",result
