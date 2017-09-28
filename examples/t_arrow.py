import arrow
import induce
lines = induce.slurplstriparg()
for l in lines:
    if not l.strip(): continue
    with induce.Tracer(l):
        dt = arrow.get(l)
