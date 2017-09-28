"""
Grammar inference module
"""
from typing import Dict, Any, List, Iterator, Tuple, ItemsView

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

def non_trivial_envdict(myvar: collections.OrderedDict) -> collections.OrderedDict:
    """
    Removes small and temporary variables -- those that
    have name length under a certain value or those that
    only contain a string under a certain length as a value.
    """
    return collections.OrderedDict([(k, v) for k, v in myvar.items() if non_trivial_val(v)])

def add_prefix(fname: str, mydict: collections.OrderedDict) -> collections.OrderedDict:
    """
    Adds a prefix (the current function name is accepted as the parameter)
    to the variable name for a dict
    """
    return collections.OrderedDict([("%s:%s" % (fname, k), v) for k, v in mydict.items()
                                    if non_trivial_val(v)])

def djs_to_string(djs: OrderedSet) -> str:
    """Convert disjoint set to string"""
    return "\n\t| ".join([i.replace('\n', '\\n') for i in sorted(djs)])

def grammar_lst(rules: collections.OrderedDict) -> List[str]:
    """
    Convert a given set of rules to their string representation
    """
    return ["%s ::= %s" % (key, djs_to_string(rules[key])) for key in rules.keys()]

def nonterm(var: str) -> str:
    """Produce a Non Terminal symbol"""
    return "$%s" % var.upper()

def strip_unused_rules(rules: collections.OrderedDict) -> collections.OrderedDict:
    """
    Strip out rules (except start) that are not in the right side.
    this has intelligence to avoid keeping circular rules
    """
    if not cfg.strip_unused_rules: return rules
    def has_key(rules: collections.OrderedDict, key: str) -> bool:
        """Check if a key is present in RHS of given set or rules"""
        for dvals in rules.values():
            for prodstr in dvals:
                if key in prodstr: return True
        return False

    new_rules = collections.OrderedDict() # type: collections.OrderedDict
    new_rules['$START'] = rules['$START']

    while True:
        new_keys = [rulevar for rulevar in sorted(rules.keys())
                    if rulevar not in new_rules.keys() and has_key(new_rules, rulevar)]
        for k in new_keys:
            new_rules[k] = rules[k]
        if not new_keys: break

    return new_rules

def get_return_value(frameenv: Dict[str, Any]) -> collections.OrderedDict:
    """
    Flatten and set the return value as caller:callee rules
    """
    my_rv = collections.OrderedDict() # type: collections.OrderedDict
    return_value = collections.OrderedDict(frameenv['arg'])
    # return_value will be a flattened dict
    if return_value:
        r_name = "%s:%s" % (frameenv['caller_name'], frameenv['func_name'])
        lst = [(key, val) for key, val in return_value.items()
               if non_trivial_val(val)]
        for key, val in lst:
            my_rv["%s_%s" % (r_name, key)] = val
    return my_rv

def most_relevant(lst: ItemsView[str, Any]) -> List[Tuple[str, Any]]:
    """
    Return the most relevant (non-nested) structures,
    especially reduce imporance of arrays
    """
    def cmp(aaa: int, bbb: int) -> int:
        """py2 cmp"""
        return (aaa > bbb) - (bbb - aaa)
    def customsort(str1: Tuple[str, Any], str2: Tuple[str, Any]) -> int:
        """Our custom sort"""
        s1_ = str1[0].count('.')
        s2_ = str2[0].count('.')
        if s1_ != s2_: return cmp(s1_, s2_)
        l1_ = len(str2[0])
        l2_ = len(str1[0])
        if l1_ != l2_: return cmp(l1_, l2_)
        if str1[0] > str2[0]: return 1
        if str2[0] > str1[0]: return -1
        return 0
    def is_array_member(k: str) -> bool:
        """Is this an array member?"""
        return len(re.findall(r'[.]\d+', k)) > 0
    my_lst = sorted(lst, key=functools.cmp_to_key(customsort))
    return [(k, v) for k, v in my_lst if not is_array_member(k)]

def get_grammar(my_input: str, local_env: collections.OrderedDict) -> collections.OrderedDict:
    """ Obtain a grammar for a specific input """
    grules = collections.OrderedDict() # type: collections.OrderedDict
    grules.setdefault("$START", OrderedSet()).add(my_input) # initial grammar

    # for each environmental variable, look for a match of its value in the
    # input string or its alternatives in each rule.
    # if found, replace the matched portion with the variable name, and add a new rule
    # to the grammar rules name -> value

    while True:
        new_rules = collections.OrderedDict() # type: collections.OrderedDict
        for envvar, envval_djs in most_relevant(local_env.items()):
            for envval in envval_djs:
                present_in_input = False
                for key, alternatives in grules.items():
                    # TODO: We need to be more intelligent here in matching.
                    # ideally, we should only look for matching rules
                    # after comparing the class.function name.
                    # the reason is that, the values from an environment
                    # disjunction is only relevant/extracted from the parameters
                    # of the current invocation of the particular function.
                    # That is, we should never replace the environment value
                    # from one function in the rule from parameters of another.
                    # doing so, risks collission.
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
    TRACE_START = 1
    TRACE_STOP = 0
    TRACE_LINE = -1

    def __init__(self) -> None:
        """ Initialize grammar """
        self.grules = collections.OrderedDict() # type: collections.OrderedDict
        self.environment = collections.OrderedDict() # type: collections.OrderedDict
        self.input_str = ''
        self.my_parameters = collections.OrderedDict() # type: collections.OrderedDict[str, Any]

    def __str__(self) -> str: return "\n".join(grammar_lst(self.grules))

    def my_params(self, fkey: str) -> Any:
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
        params = add_prefix(fname, collections.OrderedDict(frameenv['parameters']))
        # will not shadow because the format is cname.attr
        params.update(non_trivial_envdict(collections.OrderedDict(frameenv['self'])))
        # save only those parameters that are relevant (i.e present in the main input)
        self.my_parameters[fkey] = collections.OrderedDict(
            [(key, val) for key, val in params.items() if val in self.input_str])

    def add_env(self, var: str, value: Any) -> None:
        """Add var value pair to environment"""
        if non_trivial_val(value):
            self.environment.setdefault(var, OrderedSet()).add(value)

    def is_in_params(self, fkey: str, value: str) -> bool:
        """Is the given value included in the parameters of the function"""
        params = self.my_params(fkey)
        for val in params.values():
            if value in val: return True
        return False

    def trace_line(self, frameenv: Dict[str, Any]) -> None:
        """Update grammar with the frame"""
        fname = frameenv['func_name']
        fkey = '%s:%s' % (fname, frameenv['id'])

        # Save the parameters when the call is made because the parameters can
        # be overwritten subsequently.
        if frameenv['event'] == 'call':
            self.push_params(fkey, fname, frameenv)

        # now which locals to save?
        # check for non-triviality, and usefulness. Should be >2 and should be
        # part of input to this call.
        for var, value in self.my_params(fkey).items():
            self.add_env(var, value)
        for var, value in add_prefix(fname, collections.OrderedDict(frameenv['variables'])).items():
            if self.is_in_params(fkey, value):
                self.add_env(var, value)
        if frameenv['event'] == 'return':
            for var, value in get_return_value(frameenv).items():
                self.add_env(var, value)

    def trace_start(self, frameenv: Dict[str, Any]) -> None:
        """Save input at the start of a record"""
        self.input_str = frameenv['$input']

    def trace_stop(self) -> None:
        """ reset grammar at the end of a record"""
        new_grammar = get_grammar(self.input_str, self.environment)
        self.grules = merge_odicts(self.grules, new_grammar)

    def handle_events(self, jframe: Dict[str, Any]) -> int:
        """Calll correct events based on the frame"""
        if jframe['event'] == 'trace_start':
            self.trace_start(jframe)
            return Grammar.TRACE_START
        if jframe['event'] == 'trace_stop':
            self.trace_stop()
            return Grammar.TRACE_STOP
        myframe = collections.OrderedDict(sorted(jframe.items(), key=lambda x: x[0]))
        self.trace_line(myframe)
        return Grammar.TRACE_LINE

@contextmanager
def grammar(hide: bool = False) -> Iterator[Any]:
    """The context manager for grammar"""
    mygrammar = Grammar()
    yield mygrammar
    lines = "_" * 80
    if not hide: print(("%s\n%s\n%s" % (lines, mygrammar, lines)))
