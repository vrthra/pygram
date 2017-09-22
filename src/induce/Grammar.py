import sys, collections
import config as cfg
from contextlib import contextmanager
from Ordered import MultiValueDict, OrderedSet

# TODO:
# In some cases, like urlparse:url, one of the parameter names are reused as
# an entirely new variable. This needs to be handled by creating a new
# variable each time a variable is assigned to.

initialized = False

class Grammar(object):
    def __init__(self):
        self.grules = MultiValueDict()
        self.my_initial_rules = MultiValueDict()

    def reset(self):
        self.my_initial_rules = MultiValueDict()

    def input_rules(self, fkey):
        if self.my_initial_rules.get(fkey) == None:
            raise Exception("%s: input_rules event:call should have happened before this" % fkey)
        return self.my_initial_rules[fkey]


    def save_params(self, fkey, fname, frameenv):
        params = self.decorate(fname, frameenv['parameters'])
        # will not shadow because the format is cname.attr
        params.update(self.non_trivial(frameenv['self']))

        # for this function (blocks have same fnname)
        #if self.my_initial_rules.get(fkey):
        #    raise Exception("%s: this function should not have been saved before first call" % fkey) # Check and remove
        rules = MultiValueDict()
        # add rest of parameters
        for (k,v) in params.iteritems():
            rules.setdefault(self.nt(k), OrderedSet()).add(v)
        self.my_initial_rules[fkey] = rules


    def get_grammar(self, frameenv):
        """
        get_grammar gets called for each line of execution with a frame object
        that corresponds to the current environment.
        """
        fname = frameenv['func_name']
        fkey = '%s:%s' % (fname, frameenv['id'])
        params = self.decorate(fname, frameenv['parameters'])
        vself = frameenv['self']

        self.start_rule(fkey, fname, params, vself)

        # get the initial rules from parameters.
        # Here is a problem. We allow self.* as one of the inputs to a function.
        # now, if a function is invoked on the self, it would still contain the
        # entire input which gets added as a disjunction to self.input.
        # Needed: We need to consider only those variables in self that was
        # touched during the function execution.

        # Save the parameters when the call is made because the parameters can
        # be overwritten subsequently.
        if frameenv['event'] == 'call':
            self.save_params(fkey, fname, frameenv)

        if frameenv['event'] == 'line':
            # TODO: Within a particular block execution the same variable
            # normally does not take different values. This is assumed for
            # now, but this should be converted to a disjunction.
            pass

        if frameenv['event'] != 'return': return {}
        # remove the initial_rules for fkey : TODO

        my_rules = self.input_rules(fkey)

        my_local_env = MultiValueDict()
        # TODO: for self, and other objects, it may be worthwhile to use
        # self.id() as a part of decoration, because the alternatives of
        # a particular object may be different from anothe object of the
        # same class.
        my_local_env.merge_dict(self.non_trivial(frameenv['self']))
        my_local_env.merge_dict(self.decorate(fname,frameenv['variables']))

        # Set the return value
        return_value = frameenv['arg']
        if  return_value != None:
            return_name = "%s:%s" % (frameenv['caller_name'], frameenv['func_name'])
            if isinstance(return_value, dict):
                for key,value in self.non_trivial(return_value).iteritems():
                    my_local_env.setdefault("%s_%s" % (return_name, key), OrderedSet()).add(value)
            elif isinstance(return_value, list):
                for key,value in enumerate(self.non_trivial(return_value)):
                    my_local_env.setdefault("%s_%s" % (return_name, key), OrderedSet()).add(value)
            else:
                rv = self.non_trivial(return_value)
                if rv != None:
                    my_local_env.setdefault(return_name, OrderedSet()).add(rv)

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
                    if present_in_input: new_rules.setdefault(envvar,OrderedSet()).add(envval)

            for key in new_rules.keys():
                my_rules[self.nt(key)] = new_rules[key] # Add new rule to grammar
                del my_local_env[key] # Do not expand this again

            if len(new_rules) == 0: break # Nothing to expand anymore

        return self.strip_unused_self(my_rules, params, vself)

    def update(self, frameenv):
        """
        the grules contains $START and all previous iterations.
        """
        g = self.get_grammar(frameenv)
        if len(g) > 0:
            self.grules.merge(g)

    def __str__(self):
        my_rules = self.strip_unused_rules(self.grules)
        return self.grammar_to_string(my_rules)

    def strip_unused_rules(self, rules):
        # strip out rules (except start) that are not in the right side.
        # this has intelligence to avoid keeping circular rules
        if not cfg.strip_unused_rules: return rules
        def has_key(rules, key):
            for v in rules.values():
                for d in v:
                    if key in d: return True
            return False

        new_rules = MultiValueDict()
        new_rules['$START'] = rules['$START']

        while True:
            new_keys = []
            for rulevar in rules.keys():
                if rulevar in new_rules.keys(): continue
                if has_key(new_rules, rulevar):
                    new_keys.append(rulevar)
                    break
            for k in new_keys:
                new_rules[k] = rules[k]
            if len(new_keys) == 0: break

        return new_rules

    def grammar_to_string(self, rules):
        lst = ["%s ::= %s" % (key, "\n\t| ".join([i.replace('\n', '\\n') for i in rules[key]])) for key in rules.keys()]
        return "\n".join(lst)

    def nt(self, var): return "$%s" % var.upper()

    def longest_first(self, myset): return sorted([l for l in list(myset)], key=len, reverse=True)

    def non_trivial(self, d):
        if isinstance(d, dict):
            return {k:v for (k,v) in d.iteritems() if len(v) >= 2}
        elif isinstance(d, list):
            return [v for v in d if len(v) >= 2]
        elif len(d) >= 0:
            return d
        return None

    def start_rule(self, fkey, fname, params, vself):
        global initialized
        # The special-case for start symbol. This is for the entire grammar.
        # We initialize $START with the first string parameter.
        # self may also contain input values sometimes.
        if not initialized:
            paramstr = " ".join([self.nt(k) for (k,v) in params.items() + vself.items()])
            #self.grules["$START:%s" % fname] = OrderedSet([paramstr])
            self.grules["$START"] = OrderedSet([paramstr])
            initialized = True

    def decorate(self, fname, d):
        return {"%s:%s" % (fname, k):v for (k,v) in self.non_trivial(d).iteritems()}

    def strip_unused_self(self, rules, params, vself):
        if not cfg.strip_unused_self: return rules
        # params and self should not be disjunctive here.
        my_rules = rules.copy()
        for k in vself.keys():
            ntk = self.nt(k)
            if rules.get(ntk):
                v = rules[ntk]
                found = False
                for d in v:
                   if '$' in d:
                       found = True
                       break
                if not found: del my_rules[ntk]
        return my_rules

    def gc(self):
        # for each nt, expand it to the full string, and replace values that it matches.
        pass


@contextmanager
def grammar(hide=False):
    mygrammar = Grammar()
    yield mygrammar
    mygrammar.gc()
    if not hide:
      print("_" * 80)
      print(mygrammar)
      print("_" * 80)
