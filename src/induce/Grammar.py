import sys, collections
import config as cfg
from contextlib import contextmanager

class Grammar(object):
    def __init__(self):
        self.grules = MultiValueDict()
        self.environment = MultiValueDict()
        self.frameenv = MultiValueDict()

    def __str__(self): return self.grammar_to_string(self.grules)

    def grammar_to_string(self, grules):
        return "\n".join(["%s ::= %s" % (key, "\n\t| ".join(grules[key])) for key in grules.keys()])

    def nt(self, var): return "$%s" % var.upper()

    def longest_first(self, myset):
        l = sorted([i for (i,l) in list(myset)], key=len, reverse=True)
        return l

    def only_matching_strings(self, env, full_input):
        """ get only string variables (for now). """
        return [(k,v) for (k,v) in env.items() if type(v) == str and v in full_input]

    def get_initial_rules(self, fname, params, self_env, full_input):
        env = params
        env.update(self_env) # will not shadow because the format is cname.attr
        env_strings = self.only_matching_strings(env, full_input)

        rules = MultiValueDict()
        # For now, just concatenate string args and self string vars and call it the input string
        # TODO: add trivial ignores
        rules["$%s:START" % fname] = OrderedSet(" ".join( [self.nt(k) for (k,v) in env_strings]))
        for (k,v) in env_strings:
            rules.setdefault(self.nt(k), OrderedSet()).add(v)

        return rules



    def get_grammar(self, frameenv, full_input):
        """ Obtain a grammar for a specific input """
        params = frameenv['parameters']
        fname = frameenv['func_name']

        local_env = frameenv['variables']
        self_env = frameenv['self']

        my_input = self.get_relevant_input(fname, params, self_env) # TODO: self may also contain input value sometimes.

        grules = self.get_initial_rules(params, self_env, full_input)

        # for each environmental variable, look for a match of its value in the
        # input string or its alternatives in each rule.
        # if found, replace the matched portion with the variable name, and add a new rule
        # to the grammar rules name -> value

        while True:
            new_rules = MultiValueDict()
            for (envvar, envval_djs) in local_env.items():
                for envval in self.longest_first(envval_djs): # envvals are disjunctions (esp for recursive funcs)
                    present_in_input = False
                    for key, alternatives in grules.items():
                        matched = [i for i in alternatives if envval in i]
                        if len(matched) > 0: present_in_input = True
                        for m in matched:
                            alternatives.replace(m, m.replace(envval, self.nt(envvar)))
                    # TODO: should we add a disjoin here or just uuid the var if it already exists?
                    if present_in_input: new_rules.setdefault(envvar,OrderedSet()).add(envval)

            for key in new_rules.keys():
                grules[self.nt(key)] = new_rules[key] # Add new rule to grammar
                del local_env[key] # Do not expand this again

            if len(new_rules) == 0: break # Nothing to expand anymore

        return grules

    def update(self, frameenv):
        """
        update gets called at the end of __exit__ hook of the Tracer.
        """
        self.grules.merge(self.get_grammar(frameenv, full_input))

@contextmanager
def grammar(hide=False):
    mygrammar = Grammar()
    yield mygrammar
    if not hide:
      print("_" * 80)
      print("Merged grammar ->\n%s" % mygrammar)
      print("_" * 80)
