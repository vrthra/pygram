import tracer

class Grammar(object):
    def __init__(self, method, inputs):
        self.method = method
        self.inputs = inputs
        self.grammar = self.get_merged_grammar()

    # Convert a variable name into a grammar nonterminal
    def nonterminal(self, var): return "$" + var.upper()
     
    # Pretty-print a grammar
    def grammar_to_string(self, grammar):
        return "\n".join(["%s ::= %s" % (key, " | ".join(grammar[key])) for key in grammar.keys()]) + "\n"

    def __str__(self):
        return self.grammar_to_string(self.grammar)
    
    # Obtain a grammar for a specific input
    def get_grammar(self, the_input):
        # Here's our initial grammar
        grammar = {"$START": [the_input]}
    
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
                    for j in range(0, len(repl_alternatives)):
                        repl = repl_alternatives[j]
                        if value in repl:
                            # Found variable value in some grammar nonterminal
                                
                            # Replace value by nonterminal name
                            alt_key = self.nonterminal(var)
                            repl_alternatives[j] = repl.replace(value, alt_key)
                            new_rules = new_rules + [(var, alt_key, value)]
                
            if len(new_rules) == 0: break # Nothing to expand anymore
                    
            for (var, alt_key, value) in new_rules:
                # Add new rule to grammar
                grammar[alt_key] = [value]
    
                # Do not expand this again
                del the_values[var]
                                
        return grammar
    
    # Merge two grammars G1 and G2
    def merge_grammars(self, g1, g2):
        merged_grammar = g1
        for key2 in g2.keys():
            repl2 = g2[key2]
            key_found = False
            for key1 in g1.keys():
                repl1 = g1[key1]
                for repl in repl2:
                    if key1 == key2:
                        key_found = True
                        if repl not in repl1:
                            # Extend existing rule
                            merged_grammar[key1] = repl1 + [repl]
                                
            if not key_found: 
                merged_grammar[key2] = repl2
                # Add new rule
        return merged_grammar
    
    # Get a grammar for multiple inputs
    def get_merged_grammar(self):
        merged_grammar = None
        for i in self.inputs:
            grammar = self.get_grammar(i)
            print( "%s ->\n%s" % (repr(i), self.grammar_to_string(grammar)))
            if merged_grammar is None:
                merged_grammar = grammar
            else:
                merged_grammar = self.merge_grammars(merged_grammar, grammar)
    
        return merged_grammar

