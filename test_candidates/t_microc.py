import microc
import helpers, induce

with induce.grammar() as g:
    test_program_example = helpers.slurparg()
    mc = microc.MicroC()
    with induce.Tracer(test_program_example, g):
      mc.parse_text(test_program_example)
      print mc.codegen.code
