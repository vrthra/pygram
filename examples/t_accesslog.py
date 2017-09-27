import accesslog
import induce

content = induce.slurplarg()
for line in content:
    with induce.Tracer(line):
        summary = accesslog.LogAnalyzer(line, 5)
        summary.analyze()
