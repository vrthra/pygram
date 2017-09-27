import accesslog
import induce

content = induce.slurparg()
summary = accesslog.LogAnalyzer(content, 5)
with induce.Tracer(content):
    summary.analyze()
