"""
Grammar inference module
"""
from typing import Dict, Any

from contextlib import contextmanager
import collections
import config as cfg
from induce.Ordered import MultiValueDict, OrderedSet

# pylint: disable=C0321,fixme

# TODO:
# In some cases, like urlparse:url, one of the parameter names are reused as
# an entirely new variable. This needs to be handled by creating a new
# variable each time a variable is assigned to.

def non_trivial_val(val: str) -> bool:
    """ Is the variable temporary? """
    return len(val) >= 2

def non_trivial_envdict(myvar: Dict[(str, str)]) -> Dict[(str, str)]:
    """
    Removes small and temporary variables -- those that
    have name length under a certain value or those that
    only contain a string under a certain length as a value.
    """
    return {k:v for k, v in myvar.items() if non_trivial_val(v)}

def add_prefix(fname: str, mydict: Dict[(str, str)]):
    """
    Adds a prefix (the current function name is accepted as the parameter)
    to the variable name for a dict
    """
    return {"%s:%s" % (fname, k):v for k, v in mydict.items()
            if non_trivial_val(v)}

def grammar_to_string(rules):
    """
    Convert a given set of rules to their string representation
    """
    lst = ["%s ::= %s" % (key, "\n\t| ".join([i.replace('\n', '\\n')
                                              for i in rules[key]]))
           for key in rules.keys()]
    return "\n".join(lst)

def nonterm(var: str):
    """Produce a Non Terminal symbol"""
    return "$%s" % var.upper()

def longest_first(myset: set):
    """For a set return a sorted list with longest element first"""
    return sorted([l for l in myset], key=len, reverse=True)

# TODO: we really do not need to special case self
# Turn this into just normal objects.
def strip_unused_self(rules: MultiValueDict, vself: Dict[str, Any]):
    """
    Removes references to unused members of self.
    """
    if not cfg.strip_unused_self: return rules
    # params and self should not be disjunctive here.
    my_rules = rules.copy()
    for k in vself.keys():
        ntk = nonterm(k)
        if rules.get(ntk):
            prods = rules[ntk]
            found = False
            for prod in prods:
                if '$' in prod:
                    found = True
                    break
            if not found: del my_rules[ntk]
    return my_rules

def strip_unused_rules(rules: MultiValueDict):
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
        new_keys = [rulevar for rulevar in rules.keys()
                    if rulevar not in new_rules.keys() and has_key(new_rules, rulevar)]
        for k in new_keys:
            new_rules[k] = rules[k]
        if not new_keys: break

    return new_rules

def get_return_value(frameenv: Dict[(str, Any)]):
    """
    Flatten and set the return value as caller:callee rules
    """
    my_rv = MultiValueDict()
    return_value = frameenv['arg']
    # return_value will be a flattened dict
    if return_value:
        r_name = "%s:%s" % (frameenv['caller_name'], frameenv['func_name'])
        lst = [(key, val) for key, val in return_value.items()
               if non_trivial_val(val)]
        for key, val in lst:
            my_rv.setdefault("%s_%s" % (r_name, key), OrderedSet()).add(val)
    return my_rv

def get_grammar(my_input, local_env):
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
                for mat in matched:
                    alternatives.replace(mat, mat.replace(envval, nonterm(envvar)))
            if present_in_input: new_rules.setdefault(envvar, OrderedSet()).add(envval)

        for key in new_rules.keys():
            grules[nonterm(key)] = new_rules[key] # Add new rule to grammar
            del local_env[key] # Do not expand this again

        if not new_rules: break # Nothing to expand anymore

    return strip_unused_rules(grules)


class Grammar(object):
    """
    Grammar inference
    """
    def __init__(self):
        """ Initialize grammar """
        self.grules = MultiValueDict()
        self.environment = collections.OrderedDict()
        self.i = None

    def __str__(self): return grammar_to_string(self.grules)

    def add_env(self, var, value):
        """Add var value pair to environment"""
        if non_trivial_val(value):
            self.environment[var] = value

    def update(self, frameenv):
        """Update grammar with the frame"""
        self.i = frameenv['$input']
        for var, value in frameenv['string_vars']:
            if value in self.i: self.add_env(var, value)

    def reset(self):
        """ reset grammar at the end of a record"""
        self.grules.merge(get_grammar(self.i, self.environment))

@contextmanager
def grammar(hide=False):
    """The context manager for grammar"""
    mygrammar = Grammar()
    yield mygrammar
    lines = "_" * 80
    if not hide: print(("%s\n%s\n%s" % (lines, mygrammar, lines)))
