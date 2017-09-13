import accesslog
import induce, helpers

with induce.grammar() as g:
  content = helpers.slurparg()
  summary = accesslog.LogAnalyzer(content, 5)
  with induce.Tracer(content, g):
    summary.analyze()
