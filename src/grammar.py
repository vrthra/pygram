import sys
import collections

class Tracer(object):
    def __init__(self, i, v):
        self.method = self.tracer(i, v)

    def __enter__(self):
        sys.settrace(self.method)

    def __exit__(self, type, value, traceback):
        sys.settrace(None)

    def tracer(self, the_input, the_values):
        # We record all string variables and values occurring during execution
        def traceit(frame, event, arg):
            variables = frame.f_locals.keys()
            for var in variables:
                value = frame.f_locals[var]
                if isinstance(value, str) and len(value) >= 2 and value in the_input:
                    the_values[var] = value
            return traceit
        return traceit

class Multidict(collections.defaultdict):
    def merge(self, g2):
        for k,v in g2.items(): self[k] = self[k] | v

class RSet(set):
    def replace(self, key, replacement):
        self.remove(key)
        self.add(replacement)

class Grammar(object):
    def __init__(self): self.grammar = Multidict(RSet)

    def __str__(self): return self.grammar_to_string(self.grammar)

    def grammar_to_string(self, grammar):
        return "\n".join(["%s ::= %s" % (key, " | ".join(grammar[key])) for key in grammar.keys()])

    def nt(self, var): return "$" + var.upper()

    # Obtain a grammar for a specific input
    def get_grammar(self, my_input, local_values):
        # Here's our initial grammar
        grammar = {"$START": RSet([my_input])}

        # Now for each (VAR, VALUE) found:
        # 1. We search for occurrences of VALUE in the grammar
        # 2. We replace them by $VAR
        # 3. We add a new rule $VAR -> VALUE to the grammar
        while True:
            new_rules = []
            for localvar, localval in local_values.items():
                for key, inputvalues in grammar.items():
                    rules = [(self.nt(localvar), localval, ivalue) for ivalue in inputvalues if localval in ivalue]

                    for (nt_myvar, my_val, r) in rules:
                        inputvalues.replace(r, r.replace(my_val, nt_myvar))

                    new_rules += [(localvar, nt, lval) for (nt, lval, _) in rules]

            if len(new_rules) == 0: break # Nothing to expand anymore

            for (lvar, ntkey, lvalue) in new_rules:
                # Add new rule to grammar
                grammar[ntkey] = RSet([lvalue])

                # Do not expand this again
                del local_values[lvar]

        return grammar

    def update(self, i, v):
        self.grammar.merge(self.get_grammar(i, v))
