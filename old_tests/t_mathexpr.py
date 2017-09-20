import mathexpr
import induce, helpers

with induce.grammar() as g:
    exprs= helpers.slurplstriparg()
    for e in exprs:
        with induce.Tracer(e, g):
            mathexpr.Parser(e, {})
