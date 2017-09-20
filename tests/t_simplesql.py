import simplesql
import induce

data = '''\
SELECT * from XYZZY, ABC
select * from SYS.XYZZY
Select A from Sys.dual
Select A,B,C from Sys.dual
Select A, B, C from Sys.dual, Table2   
Select A from Sys.dual where a in ('RED','GREEN','BLUE')
Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)
Select A,b from table1,table2 where table1.id eq table2.id\
'''


for l in data.split('\n'):
    with induce.Tracer(l.strip()):
        simplesql.simpleSQL.parseString(l)
