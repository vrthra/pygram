
def filter_unused(grammar):
    while True:
        values = grammar.values()
        keys = set(grammar.keys())
        keys.remove('$START')
        for k in grammar.keys():
            for v in values:
                for iv in v:
                    if k in str(iv):
                        keys.remove(k)
                        break
                else:
                    continue
                break
            pass
        for k in keys:
            del grammar[k]
        if not keys:
            break
    return grammar

def get_updated_value(to_remove, v):
    for k,vs in to_remove.items():
        if v in vs:
            return k
    return v

def filter_redundant(grammar):
    kv = [(k,v) for k,v in grammar.items()]
    ks = [k for k,v in kv]
    vs = [v for k,v in kv]
    to_remove = {}
    for k in grammar.keys():
        ids = [i for i,x in enumerate(vs) if k in x]
        if ids:
            to_remove[k] = [ks[j] for j in ids if ks[j] != '$START']

    new_grammar = {}
    for k,vs in grammar.items():
        alt = set()
        for v in vs:
            val = get_updated_value(to_remove, v)
            alt.add(val)
        new_grammar[k] = alt
    return new_grammar

