"""
Grammar inference module
"""
from typing import Dict, Any, List

from contextlib import contextmanager
import functools
import re
import collections
import config as cfg
from induce.Ordered import OrderedSet, merge_odicts

# pylint: disable=C0321,fixme

# TODO:
# In some cases, like urlparse:url, one of the parameter names are reused as
# an entirely new variable. This needs to be handled by creating a new
# variable each time a variable is assigned to.

def non_trivial_val(val: str) -> bool:
    """ Is the variable temporary? """
    return len(val) >= 2

def non_trivial_envdict(myvar: Dict[str, str]) -> Dict[str, str]:
    """
    Removes small and temporary variables -- those that
    have name length under a certain value or those that
    only contain a string under a certain length as a value.
    """
    return collections.OrderedDict([(k, v) for k, v in myvar.items() if non_trivial_val(v)])

def add_prefix(fname: str, mydict: Dict[str, str]):
    """
    Adds a prefix (the current function name is accepted as the parameter)
    to the variable name for a dict
    """
    return collections.OrderedDict([("%s:%s" % (fname, k), v) for k, v in mydict.items()
                                    if non_trivial_val(v)])

def djs_to_string(djs):
    """Convert disjoint set to string"""
    return "\n\t| ".join([i.replace('\n', '\\n') for i in sorted(djs)])

def grammar_lst(rules):
    """
    Convert a given set of rules to their string representation
    """
    return sorted(["%s ::= %s" % (key, djs_to_string(rules[key])) for key in rules.keys()])

def nonterm(var: str):
    """Produce a Non Terminal symbol"""
    return "$%s" % var.upper()

def strip_unused_rules(rules: collections.OrderedDict) -> Dict[str, Any]:
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

    new_rules = collections.OrderedDict() # type: Dict[str, Any]
    new_rules['$START'] = rules['$START']

    while True:
        new_keys = [rulevar for rulevar in sorted(rules.keys())
                    if rulevar not in new_rules.keys() and has_key(new_rules, rulevar)]
        for k in new_keys:
            new_rules[k] = rules[k]
        if not new_keys: break

    return new_rules

def get_return_value(frameenv: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten and set the return value as caller:callee rules
    """
    my_rv = collections.OrderedDict() # type: Dict[str, Any]
    return_value = frameenv['arg']
    # return_value will be a flattened dict
    if return_value:
        r_name = "%s:%s" % (frameenv['caller_name'], frameenv['func_name'])
        lst = [(key, val) for key, val in return_value.items()
               if non_trivial_val(val)]
        for key, val in lst:
            my_rv["%s_%s" % (r_name, key)] = val
    return my_rv

def most_relevant(lst: List[Any]) -> List[Any]:
    """
    Return the most relevant (non-nested) structures,
    especially reduce imporance of arrays
    """
    def cmp(aaa, bbb):
        """py2 cmp"""
        return (aaa > bbb) - (bbb - aaa)
    def customsort(str1, str2):
        """Our custom sort"""
        s1_ = str1[0].count('.')
        s2_ = str2[0].count('.')
        if s1_ != s2_: return cmp(s1_, s2_)
        l1_ = len(str2[0])
        l2_ = len(str1[0])
        if l1_ != l2_: return cmp(l1_, l2_)
        return str2[0] > str1[0]
    def is_array_member(k):
        """Is this an array member?"""
        return len(re.findall(r'[.]\d+', k)) > 0
    my_lst = sorted(lst, key=functools.cmp_to_key(customsort))
    return [(k, v) for k, v in my_lst if not is_array_member(k)]

def get_grammar(my_input, local_env):
    """ Obtain a grammar for a specific input """
    grules = collections.OrderedDict()
    grules.setdefault("$START", OrderedSet()).add(my_input) # initial grammar

    # for each environmental variable, look for a match of its value in the
    # input string or its alternatives in each rule.
    # if found, replace the matched portion with the variable name, and add a new rule
    # to the grammar rules name -> value

    while True:
        new_rules = collections.OrderedDict()
        for envvar, envval_djs in most_relevant(local_env.items()):
            for envval in envval_djs:
                present_in_input = False
                for key, alternatives in grules.items():
                    matched = [i for i in alternatives if envval in i]
                    if matched: present_in_input = True
                    for mat in matched:
                        # careful here TODO.
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
        self.grules = collections.OrderedDict()
        self.environment = collections.OrderedDict()
        self.input_str = None
        self.my_parameters = collections.OrderedDict()

    def __str__(self): return "\n".join(grammar_lst(self.grules))

    def my_params(self, fkey: str):
        """
        Get the set of input rules from previously saved parameters
        """
        if self.my_parameters.get(fkey) is None:
            raise Exception("%s: my_params event:call should have happened before this" % fkey)
        return self.my_parameters[fkey]


    def pop_params(self, fkey: str) -> None:
        """
        Remove the current set of parameters
        """
        del self.my_parameters[fkey]

    def push_params(self, fkey: str, fname: str, frameenv: Dict[str, Any]) -> None:
        """
        Save the current state of parameters for input rules to a function
        """
        params = add_prefix(fname, frameenv['parameters'])
        # will not shadow because the format is cname.attr
        params.update(non_trivial_envdict(frameenv['self']))
        # save only those parameters that are relevant (i.e present in the main input)
        self.my_parameters[fkey] = collections.OrderedDict(
            [(key, val) for key, val in params.items() if val in self.input_str])

    def add_env(self, var, value):
        """Add var value pair to environment"""
        if non_trivial_val(value):
            self.environment.setdefault(var, OrderedSet()).add(value)

    def is_in_params(self, fkey, value):
        """Is the given value included in the parameters of the function"""
        params = self.my_params(fkey)
        for val in params.values():
            if value in val: return True
        return False

    def update(self, frameenv):
        """Update grammar with the frame"""
        fname = frameenv['func_name']
        fkey = '%s:%s' % (fname, frameenv['id'])
        self.input_str = frameenv['$input']

        # Save the parameters when the call is made because the parameters can
        # be overwritten subsequently.
        if frameenv['event'] == 'call':
            self.push_params(fkey, fname, frameenv)

        # now which locals to save?
        # check for non-triviality, and usefulness. Should be >2 and should be
        # part of input to this call.
        for var, value in self.my_params(fkey).items():
            self.add_env(var, value)
        for var, value in frameenv['variables'].items():
            if self.is_in_params(fkey, value):
                self.add_env(var, value)
        if frameenv['event'] == 'return':
            for var, value in get_return_value(frameenv).items():
                self.add_env(var, value)

    def reset(self):
        """ reset grammar at the end of a record"""
        new_grammar = get_grammar(self.input_str, self.environment)
        self.grules = merge_odicts(self.grules, new_grammar)

@contextmanager
def grammar(hide=False):
    """The context manager for grammar"""
    mygrammar = Grammar()
    yield mygrammar
    lines = "_" * 80
    if not hide: print(("%s\n%s\n%s" % (lines, mygrammar, lines)))
