import sys, collections
import config as cfg
from contextlib import contextmanager

class Grammar(object):
    def __init__(self):
        self.grules = Multidict(RSet)
        self.environment = Multidict(RSet)

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
        """
        if cfg.non_trivial(var, value): self.environment[var].add((value, loc))

    def get_grammar(self, my_input, local_env):
        """ Obtain a grammar for a specific input """
        grules = {"$START": RSet([my_input])} # initial grammar

        # for each environmental variable, look for a match of its value in the
        # input string or its alternatives in each rule.
        # if found, replace the matched portion with the variable name, and add a new rule
        # to the grammar rules name -> value

        while True:
            new_rules = Multidict(RSet)
            for (envvar, envval_djs) in local_env.items():
                for envval in self.longest_first(envval_djs): # envvals are disjunctions (esp for recursive funcs)
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

class Tracer(object):
    """ The context manager that manages trace hooking and unhooking. """
    def __init__(self, i, g):
        self.method = self.tracer()
        self.input, self.grammar = i, g

    def __enter__(self):
        """ set hook """
        sys.settrace(self.method)

    def __exit__(self, type, value, traceback):
        """ unhook """
        sys.settrace(None)
        self.grammar.update(self.input)

    def add_if_found(self, var, value, loc):
        """ if the value of the variable was found in the input, add it to the current environment"""
        if value in self.input: self.grammar.add_env(var, value, loc)

    def sel_vars(self, env):
        """ get only string variables (for now). """
        return [(k,v) for (k,v) in env.items() if type(v) == str]

    def getmembers(self, obj):
        """ get member attributes of a self variable """
        if obj == None or not hasattr(obj, '__dict__'): return {}
        n = type(obj).__name__
        return { "%s:%s" % (n, v):v for (k,v)  in vars(obj)}


    def process_frame(self, frame, loc):
        """
        Does nothing but get all the var=value pairs from the current environment. Various
        configuration options control which scopes are checked.
        """
        # dont process if the frame is tracer
        # this happens at the end of trace -- Tracer.__exit__
        vself  = frame.f_locals.get('self')
        if type(vself) in [Tracer, Grammar]: return

        # TODO: we need to also take care of values assigned in dicts/arrays
        # TODO: also ensure that we save the parameters=value.
        env = frame.f_globals.copy() if cfg.check_globals else {}
        env.update(frame.f_locals) # the globals are shadowed.
        env.update(self.getmembers(vself) if cfg.check_self else {})

        for var, value in self.sel_vars(env): self.add_if_found(var, value, loc)

    def tracer(self):
        def loc(caller): return (caller.f_code.co_name, caller.f_code.co_filename, caller.f_lineno)

        def traceit(frame, event, arg):
            (n, f, l) = loc(frame)
            if not cfg.in_scope(f): return
            if cfg.extra_verbose:
                (cn, cf, cl) = loc(frame.f_back)
                print('%s() %s:%s\n\t%s()<- %s:%s' % (n, f, l, cn, cf, cl))

            self.process_frame(frame, (n, f, l))
            return traceit
        return traceit

class Multidict(collections.defaultdict):
    def merge(self, g2):
        for k,v in g2.items(): self[k] = self[k] | v

class RSet(set):
    def replace(self, key, replacement):
        self.remove(key)
        self.add(replacement)

@contextmanager
def grammar(hide=False):
    mygrammar = Grammar()
    yield mygrammar
    if not hide:
      print("_" * 80)
      print("Merged grammar ->\n%s" % mygrammar)
      print("_" * 80)
