import sys, collections
import config as cfg
from contextlib import contextmanager
from Ordered import MultiValueDict, OrderedSet

class Grammar(object):
    def __init__(self):
        self.grules = MultiValueDict()
        self.environment = MultiValueDict()
        self.frameenv = MultiValueDict()
        self.initialized = False
        self.my_initial_rules = MultiValueDict()

    def initial_rules(self, fkey):
        fname = self.frameenv[fkey]['func_name']
        params = self.frameenv[fkey]['parameters']
        params.update(self.frameenv[fkey]['self']) # will not shadow because the format is cname.attr

        # The special-case for start symbol. This is for the entire grammar.
        # We initialize $START with the first string parameter.
        # self may also contain input values sometimes.
        if not self.initialized:
            self.grules["$START:%s" % fname] = OrderedSet([" ".join([self.nt(k) for (k,v) in params.iteritems()])])
            self.initialized = True

        # for this function
        if not hasattr(self.my_initial_rules, fname):
            rules = MultiValueDict()
            # add rest of parameters
            for (k,v) in params.iteritems():
                rules.setdefault(self.nt(k), OrderedSet()).add(v)
            self.my_initial_rules[fname] = rules

        return self.my_initial_rules[fname]

    def decorate(self, fname, d):
        return {"%s:%s" % (fname, k):v for (k,v) in self.non_trivial(d).iteritems()}

    def get_grammar(self, frameenv):
        """
        get_grammar gets called for each line of execution with a frame object
        that corresponds to the current environment.
        """
        my_local_env = MultiValueDict()
        fname = frameenv['func_name']
        fkey = '%s:%s' % (fname, frameenv['id'])
        if self.frameenv.get(fkey) == None:
           # first activation. Save all interesting stuff
           self.frameenv[fkey] = {}
           self.frameenv[fkey]['parameters'] = self.decorate(fname, frameenv['parameters'])
           self.frameenv[fkey]['func_name'] = frameenv['func_name']
           self.frameenv[fkey]['self'] = self.non_trivial(frameenv['self'])
        else:
           my_local_env.merge_dict(self.non_trivial(frameenv['self']))
        my_local_env.merge_dict(self.decorate(fname,frameenv['variables']))

        # get the initial rules from parameters.
        my_rules = self.initial_rules(fkey)

        # for each environmental variable, look for a match of its value in the
        # input string or its alternatives in each rule.
        # if found, replace the matched portion with the variable name, and add a new rule
        # to the grammar rules name -> value

        while True:
            new_rules = MultiValueDict()
            for (envvar, envval_djs) in my_local_env.iteritems():
                for envval in self.longest_first(envval_djs): # envvals are disjunctions (esp for recursive funcs)
                    present_in_input = False
                    for key, alternatives in my_rules.iteritems():
                        matched = [i for i in alternatives if envval in i]
                        if len(matched) > 0: present_in_input = True
                        for m in matched:
                            alternatives.replace(m, m.replace(envval, self.nt(envvar)))
                    # TODO: should we add a disjoin here or just uuid the var if it already exists?
                    if present_in_input: new_rules.setdefault(envvar,OrderedSet()).add(envval)

            for key in new_rules.keys():
                my_rules[self.nt(key)] = new_rules[key] # Add new rule to grammar
                del my_local_env[key] # Do not expand this again

            if len(new_rules) == 0: break # Nothing to expand anymore

        return my_rules

    def update(self, frameenv):
        """
        the grules contains $START and all previous iterations.
        """
        self.grules = self.get_grammar(frameenv)
        #TODO: fixit self.grules.merge(self.get_grammar(frameenv))

    def __str__(self):
        return self.grammar_to_string(self.grules)

    def grammar_to_string(self, grules):
        return "\n".join(["%s ::= %s" % (key, "\n\t| ".join(grules[key])) for key in grules.keys()])

    def nt(self, var): return "$%s" % var.upper()

    def longest_first(self, myset):
        l = sorted([l for l in list(myset)], key=len, reverse=True)
        return l

    def non_trivial(self, d):
        return {k:v for (k,v) in d.iteritems() if len(v) >= 2}


@contextmanager
def grammar(hide=False):
    mygrammar = Grammar()
    yield mygrammar
    if not hide:
      print("_" * 80)
      print("Merged grammar ->\n%s" % mygrammar)
      print("_" * 80)
