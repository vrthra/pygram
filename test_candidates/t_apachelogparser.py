import apache_log_parser
from pprint import pprint
import induce, helpers

with induce.grammar() as g:
    logs = helpers.slurplstriparg()
    for line in logs:
        with induce.Tracer(line, g):
           line_parser = apache_log_parser.make_parser("%h <<%P>> %t %Dus \"%r\" %>s %b  \"%{Referer}i\" \"%{User-Agent}i\" %l %u")
           log_line_data = line_parser(line)
           pprint(log_line_data)
