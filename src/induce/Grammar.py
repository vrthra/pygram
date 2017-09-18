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

    def add_env(self, var, value, loc):
        """
        Add a newly found variable to our list. Ensure that older variables by same name are
        not overwritten.
        TODO: Should we treat recursion differently from shadowing?
        TODO: i.e func_name:varname disjoins func_name:varname but not another_func_name:varname
        """
        if cfg.non_trivial(var, value): self.environment.setdefault(var, OrderedSet()).add((value, loc))

    def add_frame(self, frameid, frame):
        """ if the frame.id alredy exists, merge this like add_env.
            Expect frame.id, frame.func_name, and frame.parameters and frame.self to remain same.
            in the frameenv['variables'] each variable, if it exists already, becomes a disjunction,
            else it becomes a single element set.
        """
         if self.frameenv.get(frameid) == None:
            self.frameenv[frameid] = frame
         else:
            self.frameenv[frameid]['variables'].merge(frame['variables'])
            self.frameenv[frameid]['self'].merge(frame['self'])

    def get_grammar(self, my_input, local_env):
        """ Obtain a grammar for a specific input """
        grules = MultiValueDict()
        # TODO: Restrict the input to only parameters of the function, and associated grules in this iteration.
        # Not the complete input in grules.

        # Replace my_input with function parameters.
        grules["$START"] = OrderedSet([my_input]) # initial grammar

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

    def update(self, i):
         self.grules.merge(self.get_grammar(i, self.environment))

@contextmanager
def grammar(hide=False):
    mygrammar = Grammar()
    yield mygrammar
    if not hide:
      print("_" * 80)
      print("Merged grammar ->\n%s" % mygrammar)
      print("_" * 80)
