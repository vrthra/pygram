import config as cfg
from contextlib import contextmanager
import collections
from induce.Ordered import MultiValueDict, OrderedSet

class Grammar(object):
    def __init__(self):
        self.grules = MultiValueDict()
        self.environment = collections.OrderedDict()
        self.i = None

    def __str__(self): return self.grammar_to_string(self.grules)

    def grammar_to_string(self, grules):
        lst = ["%s ::= %s" % (key, "\n\t| ".join([i.replace('\n', '\\n')
                                                  for i in grules[key]]))
               for key in grules.keys()]
        return "\n".join(lst)

    def longest_first(self, myset: set):
        """For a set return a sorted list with longest element first"""
        return sorted([l for l in myset], key=len, reverse=True)

    def strip_unused_rules(self, rules):
        """
        Strip out rules (except start) that are not in the right side.
        this has intelligence to avoid keeping circular rules
        """
        if not cfg.strip_unused_rules: return rules
        def has_key(rules, key):
            """Check if a key is present in RHS of given set or rules"""
            for dvals in rules.values():
                for prodstr in dvals:
                    if key in prodstr: return True
            return False

        new_rules = MultiValueDict()
        new_rules['$START'] = rules['$START']

        while True:
            new_keys = [rulevar for rulevar in sorted(rules.keys())
                        if rulevar not in new_rules.keys() and has_key(new_rules, rulevar)]
            for k in new_keys:
                new_rules[k] = rules[k]
            if not new_keys: break

        return new_rules

    def nonterm(self, var): return "$%s" % var.upper()

    def add_env(self, var, value):
        if cfg.non_trivial(var, value):
            self.environment[var] = value

    def get_grammar(self, my_input, local_env):
        """ Obtain a grammar for a specific input """
        grules = MultiValueDict()
        grules.setdefault("$START", OrderedSet()).add(my_input) # initial grammar

        # for each environmental variable, look for a match of its value in the
        # input string or its alternatives in each rule.
        # if found, replace the matched portion with the variable name, and add a new rule
        # to the grammar rules name -> value

        while True:
            new_rules = MultiValueDict()
            for envvar, envval in local_env.items():
                present_in_input = False
                for key, alternatives in grules.items():
                    matched = [i for i in alternatives if envval in i]
                    if matched: present_in_input = True
                    for m in matched:
                        alternatives.replace(m, m.replace(envval, self.nonterm(envvar)))
                if present_in_input: new_rules.setdefault(envvar, OrderedSet()).add(envval)

            for key in new_rules.keys():
                grules[self.nonterm(key)] = new_rules[key] # Add new rule to grammar
                del local_env[key] # Do not expand this again

            if len(new_rules) == 0: break # Nothing to expand anymore

        return self.strip_unused_rules(grules)

    def update(self, frameenv):
        self.i = frameenv['$input']
        for var, value in frameenv['string_vars']:
            if value in self.i: self.add_env(var, value)

    def reset(self):
        self.grules.merge(self.get_grammar(self.i, self.environment))

@contextmanager
def grammar(hide=False):
    mygrammar = Grammar()
    yield mygrammar
    lines = "_" * 80
    if not hide: print(("%s\n%s\n%s" % (lines, mygrammar, lines)))
