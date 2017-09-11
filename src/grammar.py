import tracer

class Grammar(object):
    def __init__(self, method, inputs):
        self.method = method
        self.inputs = inputs
        self.grammar = self.get_merged_grammar()

    def __str__(self): return self.grammar_to_string(self.grammar)

    def grammar_to_string(self, grammar):
        return "\n".join(["%s ::= %s" % (key, " | ".join(grammar[key])) for key in grammar.keys()])

    def nonterminal(self, var): return "$" + var.upper()

    def merge_hash(self, g1, g2):
        return {k: g1.get(k, set()) | g2.get(k, set()) for k in set(g1.keys() + g2.keys())}

    # Obtain a grammar for a specific input
    def get_grammar(self, the_input):
        # Here's our initial grammar
        grammar = {"$START": set([the_input])}

        # We obtain a mapping of variables to values
        # We store individual variable/value pairs here
        the_values = {}

        # We record all string variables and values occurring during execution
        def traceit(frame, event, arg):
            variables = frame.f_locals.keys()
            for var in variables:
                value = frame.f_locals[var]
                # print(var, value)
                # Save all non-trivial string values that also occur in the input
                if type(value) == type('') and len(value) >= 2 and value in the_input:
                    the_values[var] = value

            return traceit

        with tracer.Tracer(traceit): self.method(the_input)

        # Now for each (VAR, VALUE) found:
        # 1. We search for occurrences of VALUE in the grammar
        # 2. We replace them by $VAR
        # 3. We add a new rule $VAR -> VALUE to the grammar
        while True:
            new_rules = []
            for var in the_values.keys():
                value = the_values[var]
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
                del the_values[var]

        return grammar


    # Get a grammar for multiple inputs
    def get_merged_grammar(self):
        merged_grammar = {}
        for i in self.inputs:
            merged_grammar = self.merge_hash(merged_grammar, self.get_grammar(i))

        return merged_grammar

