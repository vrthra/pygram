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
        params = self.frameenv[fkey]['parameters'].copy()
        params.update(self.frameenv[fkey]['self']) # will not shadow because the format is cname.attr

        # for this function
        if not hasattr(self.my_initial_rules, fname):
            rules = MultiValueDict()
            # add rest of parameters
            for (k,v) in params.iteritems():
                rules.setdefault(self.nt(k), OrderedSet()).add(v)
            self.my_initial_rules[fname] = rules

        return self.my_initial_rules[fname]

    def init_start_rule(self, fkey, fname, params, vself):
        # The special-case for start symbol. This is for the entire grammar.
        # We initialize $START with the first string parameter.
        # self may also contain input values sometimes.
        if not self.initialized:
            paramstr = " ".join([self.nt(k) for (k,v) in params.items() + vself.items()])
            self.grules["$START:%s" % fname] = OrderedSet([paramstr])
            self.initialized = True

    def decorate(self, fname, d):
        return {"%s:%s" % (fname, k):v for (k,v) in self.non_trivial(d).iteritems()}

    def strip_unused_params(self, rules, params, vself):
        # params and self should not be disjunctive here.
        my_rules = rules.copy()
        for k in vself.keys():
            ntk = self.nt(k)
            if rules.get(ntk):
                v = rules[ntk]
                found = False
                for d in v:
                   if '$' in d: found = True
                   if not found: del my_rules[ntk]
        return my_rules

    def get_grammar(self, frameenv):
        """
        get_grammar gets called for each line of execution with a frame object
        that corresponds to the current environment.
        """
        fname = frameenv['func_name']
        fkey = '%s:%s' % (fname, frameenv['id'])
        params = self.decorate(fname, frameenv['parameters'])
        vself = frameenv['self']
        self.init_start_rule(fkey, fname, params, vself)

        # TODO: Within a particular block execution the same variable
        # normally not take different values. This is assumed for now, but this should be converted to a disjunction.
        if frameenv['event'] != 'return': return {}

        my_local_env = MultiValueDict()

        if self.frameenv.get(fkey) == None:
           # first activation. Save all interesting stuff
           self.frameenv[fkey] = {}
           self.frameenv[fkey]['parameters'] = self.decorate(fname, frameenv['parameters'])
           self.frameenv[fkey]['func_name'] = frameenv['func_name']
           self.frameenv[fkey]['self'] = self.non_trivial(frameenv['self'])
        else:
           my_local_env.merge_dict(self.non_trivial(frameenv['self']))


        # get the initial rules from parameters.
        # Here is a problem. We allow self.* as one of the inputs to a function.
        # now, if a function is invoked on the self, it would still contain the entire input
        # which gets added as a disjunction to self.input. Needed: We need to consider only
        # those variables in self that was touched during the function execution.
        my_rules = self.initial_rules(fkey)

        my_local_env.merge_dict(self.decorate(fname,frameenv['variables']))

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

        return self.strip_unused_params(my_rules, params, vself)

    def update(self, frameenv):
        """
        the grules contains $START and all previous iterations.
        """
        g = self.get_grammar(frameenv)
        if len(g) > 0:
            self.grules.merge(g)

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
