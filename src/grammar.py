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

class Grammar(object):
    def __init__(self): self.grammar = Multidict(set)

    def __str__(self): return self.grammar_to_string(self.grammar)

    def grammar_to_string(self, grammar):
        return "\n".join(["%s ::= %s" % (key, " | ".join(grammar[key])) for key in grammar.keys()])

    def nonterminal(self, var): return "$" + var.upper()

    # Obtain a grammar for a specific input
    def get_grammar(self, my_input, my_values):
        # Here's our initial grammar
        grammar = {"$START": set([my_input])}

        # Now for each (VAR, VALUE) found:
        # 1. We search for occurrences of VALUE in the grammar
        # 2. We replace them by $VAR
        # 3. We add a new rule $VAR -> VALUE to the grammar
        while True:
            new_rules = []
            for var, value in my_values.items():
                for key, val in grammar.items():
                    myvalues = val
                    values_to_replace = [s for s in val if value in s]
                    for repl in values_to_replace:
                        myvalues.remove(repl)

                        alt_key = self.nonterminal(var)
                        myvalues.add(repl.replace(value, alt_key))

                        new_rules += [(var, alt_key, value)]

            if len(new_rules) == 0: break # Nothing to expand anymore

            for (var, alt_key, value) in new_rules:
                # Add new rule to grammar
                grammar[alt_key] = set([value])

                # Do not expand this again
                del my_values[var]

        return grammar

    def update(self, i, v):
        self.grammar.merge(self.get_grammar(i, v))
