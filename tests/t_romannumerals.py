import romannumerals
import induce, helpers

with induce.grammar() as g:
    for rn in helpers.slurplstriparg():
      with induce.Tracer(rn, g):
        romannumerals.romanNumeral.parseString(rn)

