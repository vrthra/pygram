from pyparsing import CaselessKeyword, delimitedList, Each, Forward, Group, \
        Optional, Word, alphas,alphanums, nums, oneOf, ZeroOrMore, quotedString # , Upcase

keywords = ["select", "from", "where", "group by", "order by", "and", "or"]
[select, _from, where, groupby, orderby, _and, _or] = [ CaselessKeyword(word)
        for word in keywords ]

table = column = Word(alphas)
columns = Group(delimitedList(column))
columnVal = (nums | quotedString)

whereCond = (column + oneOf("= != < > >= <=") + columnVal)
whereExpr = whereCond + ZeroOrMore((_and | _or) + whereCond)

selectStmt = Forward().setName("select statement")
selectStmt << (select +
        ('*' | columns).setResultsName("columns") +
        _from +
        table.setResultsName("table") +
        Optional(where + Group(whereExpr), '').setResultsName("where").setDebug(False) +
        Each([Optional(groupby + columns("groupby"),'').setDebug(False),
            Optional(orderby + columns("orderby"),'').setDebug(False)
            ])
        )

