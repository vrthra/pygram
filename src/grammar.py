import sys

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
                # Save all non-trivial string values that also occur in the input
                if isinstance(value, str) and len(value) >= 2 and value in the_input:
                    the_values[var] = value
            return traceit
        return traceit

class Grammar(object):
    def __init__(self): self.grammar = {}

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
            for var in my_values.keys():
                value = my_values[var]
                for key in grammar.keys():
                    repl_alternatives = grammar[key]
                    for repl in repl_alternatives:
                        if value in repl:
                            # Found variable value in some grammar nonterminal

                            # Replace value by nonterminal name
                            alt_key = self.nonterminal(var)
                            repl_alternatives.remove(repl)
                            repl_alternatives.add(repl.replace(value, alt_key))
                            new_rules = new_rules + [(var, alt_key, value)]

            if len(new_rules) == 0: break # Nothing to expand anymore

            for (var, alt_key, value) in new_rules:
                # Add new rule to grammar
                grammar[alt_key] = set([value])

                # Do not expand this again
                del my_values[var]

        return grammar

    def merge_hash(self, g1, g2):
        return {k: g1.get(k, set()) | g2.get(k, set()) for k in set(g1.keys() + g2.keys())}

    def update(self, i, v):
        self.grammar = self.merge_hash(self.grammar, self.get_grammar(i, v))
