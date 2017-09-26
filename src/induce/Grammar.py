import config as cfg
from contextlib import contextmanager
from induce.Ordered import Multidict, RSet

class Grammar(object):
    def __init__(self):
        self.grules = Multidict(RSet)
        self.environment = {}

    def __str__(self): return self.grammar_to_string(self.grules)

    def grammar_to_string(self, grules):
        return "\n".join(["%s ::= %s" % (key, "\n\t| ".join(grules[key])) for key in grules.keys()])

    def nt(self, var): return "$%s" % var.upper()

    def add_env(self, var, value):
        if cfg.non_trivial(var, value): self.environment[var] = value

    def get_grammar(self, my_input, local_env):
        """ Obtain a grammar for a specific input """
        grules = {"$START": RSet([my_input])} # initial grammar

        # for each environmental variable, look for a match of its value in the
        # input string or its alternatives in each rule.
        # if found, replace the matched portion with the variable name, and add a new rule
        # to the grammar rules name -> value

        while True:
            new_rules = Multidict(RSet)
            for (envvar, envval) in local_env.items():
                present_in_input = False
                for key, alternatives in grules.items():
                    matched = [i for i in alternatives if envval in i]
                    if len(matched) > 0: present_in_input = True
                    for m in matched:
                        alternatives.replace(m, m.replace(envval, self.nt(envvar)))
                if present_in_input: new_rules[envvar].add(envval)

            for key in new_rules.keys():
                grules[self.nt(key)] = new_rules[key] # Add new rule to grammar
                del local_env[key] # Do not expand this again

            if len(new_rules) == 0: break # Nothing to expand anymore

        return grules

    def update(self, i):
         self.grules.merge(self.get_grammar(i, self.environment))

@contextmanager
def grammar():
    mygrammar = Grammar()
    yield mygrammar
    print("_" * 80)
    print("Merged grammar ->\n%s" % mygrammar)
    print("_" * 80)
