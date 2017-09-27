from datetime import datetime
import induce

for l in induce.slurplstriparg():
    if l.strip() == '': continue
    dat, fmt = l.split('|')
    with induce.Tracer(l):
       datetime.strptime(dat, fmt)
