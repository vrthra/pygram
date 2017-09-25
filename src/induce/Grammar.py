"""
Grammar inference module
"""
from typing import Dict, Any

from contextlib import contextmanager
import itertools
import config as cfg
from induce.Ordered import MultiValueDict, OrderedSet


# pylint: disable=C0321,fixme

# TODO:
# In some cases, like urlparse:url, one of the parameter names are reused as
# an entirely new variable. This needs to be handled by creating a new
# variable each time a variable is assigned to.

# TODO: use mypy

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
def strip_unused_self(rules, vself):
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

def strip_unused_rules(rules):
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
    if return_value:
        return_name = "%s:%s" % (frameenv['caller_name'], frameenv['func_name'])
        if isinstance(return_value, dict):
            lst = [(key, val) for key, val in return_value.items()
                   if non_trivial_val(val)]
            for key, val in lst:
                my_rv.setdefault("%s_%s" % (return_name, key), OrderedSet()).add(val)
        elif isinstance(return_value, list):
            lst = [(key, val) for key, val in enumerate(return_value)
                   if non_trivial_val(val)]
            for key, val in lst:
                my_rv.setdefault("%s_%s" % (return_name, key), OrderedSet()).add(val)
        else:
            if non_trivial_val(return_value):
                my_rv.setdefault(return_name, OrderedSet()).add(return_value)
    return my_rv


class Grammar:
    """
    Grammar inference
    """
    def __init__(self) -> None:
        self.grules = MultiValueDict()
        self.my_initial_rules = MultiValueDict()

        # initialized is not reset at self.reset()
        # it is only once for a complete grammar.
        self.initialized = False

    def reset(self) -> None:
        """
        Reset grammar inference for the next round
        """
        self.my_initial_rules = MultiValueDict()

    def input_rules(self, fkey: str):
        """
        Get the set of input rules from previously saved parameters
        """
        if self.my_initial_rules.get(fkey) is None:
            raise Exception("%s: input_rules event:call should have happened before this" % fkey)
        return self.my_initial_rules[fkey]


    def save_params(self, fkey: str, fname: str, frameenv: Dict[str, Any]) -> None:
        """
        Save the current state of parameters for input rules to a function
        """
        params = add_prefix(fname, frameenv['parameters'])
        # will not shadow because the format is cname.attr
        params.update(non_trivial_envdict(frameenv['self']))
        rules = MultiValueDict()
        # add rest of parameters
        for (key, val) in params.items():
            rules.setdefault(nonterm(key), OrderedSet()).add(val)
        self.my_initial_rules[fkey] = rules

    def find_inclusions(self, fkey: str, my_local_env: MultiValueDict) -> MultiValueDict:
        """
        For each environmental variable, look for a match of its value in the
        input string or its alternatives in each rule.
        if found, replace the matched portion with the variable name, and add a new rule
        to the grammar rules name -> value
        """

        my_rules = self.input_rules(fkey)
        while True:
            new_rules = MultiValueDict()
            for (envvar, envval_djs) in my_local_env.items():
                for envval in longest_first(envval_djs):
                    # envvals are disjunctions (esp for recursive funcs)
                    present_in_input = False
                    for key, alternatives in my_rules.items():
                        matched = [i for i in alternatives if envval in i]
                        if matched: present_in_input = True
                        for rstr in matched:
                            alternatives.replace(rstr, rstr.replace(envval, nonterm(envvar)))
                    if present_in_input: new_rules.setdefault(envvar, OrderedSet()).add(envval)

            for key in new_rules.keys():
                my_rules[nonterm(key)] = new_rules[key] # Add new rule to grammar
                del my_local_env[key] # Do not expand this again

            if not new_rules: break # Nothing to expand anymore
        return my_rules


    def get_grammar(self, frameenv: Dict[str, Any]) -> MultiValueDict:
        """
        get_grammar gets called for each line of execution with a frame object
        that corresponds to the current environment.
        """
        self.start_rule(frameenv)

        # get the initial rules from parameters.
        # Here is a problem. We allow self.* as one of the inputs to a function.
        # now, if a function is invoked on the self, it would still contain the
        # entire input which gets added as a disjunction to self.input.
        # Needed: We need to consider only those variables in self that was
        # touched during the function execution.

        fname = frameenv['func_name']
        fkey = '%s:%s' % (fname, frameenv['id'])

        # Save the parameters when the call is made because the parameters can
        # be overwritten subsequently.
        if frameenv['event'] == 'call':
            self.save_params(fkey, fname, frameenv)

        if frameenv['event'] == 'line':
            # TODO: Within a particular block execution the same variable
            # normally does not take different values. This is assumed for
            # now, but this should be converted to a disjunction.
            pass

        if frameenv['event'] != 'return': return MultiValueDict()
        # remove the initial_rules for fkey : TODO

        my_local_env = MultiValueDict()
        # TODO: for self, and other objects, it may be worthwhile to use
        # self.id() as a part of decoration, because the alternatives of
        # a particular object may be different from anothe object of the
        # same class.
        my_local_env.merge_dict(non_trivial_envdict(frameenv['self']))
        my_local_env.merge_dict(add_prefix(fname, frameenv['variables']))

        # Set the return value
        my_rv = get_return_value(frameenv)
        my_local_env.merge(my_rv)

        my_rules = self.find_inclusions(fkey, my_local_env)
        return strip_unused_self(my_rules, frameenv['self'])

    def update(self, frameenv: Dict[str, Any]) -> None:
        """
        The self.grules contains $START and all previous iterations.
        """
        rules = self.get_grammar(frameenv)
        self.grules.merge(rules)

    def __str__(self):
        my_rules = strip_unused_rules(self.grules)
        return grammar_to_string(my_rules)

    def start_rule(self, frameenv: Dict[str, Any]) -> None:
        """
        The special-case for start symbol. This is for the entire grammar.
        We initialize $START with the first string parameter.
        self may also contain input values sometimes.
        """
        if not self.initialized:
            fname = frameenv['func_name']
            params = add_prefix(fname, frameenv['parameters'])
            vself = frameenv['self']
            lstvars = itertools.chain(params.items(), vself.items())
            paramstr = " ".join([nonterm(k) for (k, _) in lstvars])
            self.grules["$START"] = OrderedSet([paramstr])
            self.initialized = True

    def ggc(self) -> None:
        """
        TODO: Remove rules that do not have a disjunction
        """
        pass


@contextmanager
def grammar(hide=False):
    """
    The grammar context manager. Use `with induce.grammar() as g:`
    """
    mygrammar = Grammar()
    yield mygrammar
    mygrammar.ggc()
    lines = "_" * 80
    if not hide: print(("%s\n%s\n%s" % (lines, mygrammar, lines)))
