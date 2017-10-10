"""
Grammar Refiner module
"""

from typing import List, Any
import sys
import collections
import re
from induce.Ordered import OrderedSet, merge_odicts

def djs_to_string(djs: OrderedSet) -> str:
    """Convert disjoint set to string"""
    return "\n\t| ".join([i.replace('\n', '\\n') for i in sorted(djs)])

def grammar_lst(rules: collections.OrderedDict) -> List[str]:
    """
    Convert a given set of rules to their string representation
    """
    return ["%s ::=\n\t| %s" % (key, djs_to_string(rules[key])) for key in rules.keys()]

class Refiner:
    """
    Refine gramamr
    """
    def __init__(self) -> None:
        """ Initialize refiner with grammar """
        self.my_grammar = collections.OrderedDict() # type: collections.OrderedDict

    def add_rules(self, rules: List[Any]):
        """ Add new rules from an invocation"""
        for rkey, rval in rules:
            self.my_grammar.setdefault(rkey, OrderedSet()).add(rval)

    def tree(self, ptree):
        self.parent_tree = ptree

    def __str__(self) -> str:
        lst = self.simplify(self.my_grammar)
        # lst = self.my_grammar
        return "\n".join(grammar_lst(lst))

    def is_parent(self, parent_v, child_v):
        child = self.extract_fn(child_v)
        if not child: return False
        parent = self.extract_fn(parent_v)
        nxt = self.parent_tree.get(child)
        while nxt and parent not in nxt:
            assert len(nxt) == 1
            nxt = self.parent_tree.get(nxt[0])
        return nxt is not None

    def extract_fn(self, mystr):
        val = re.search('^.+\[(.+),[0-9]+\]$', mystr)
        if val: return val.group(1)
        return None

    def replace_def_of_key_with_value_def(self, lst, rules):
        # thus deleting the value
        for key, value in lst:
            rules[key] = rules[value]
            del rules[value]
        return rules

    def replace_use_of_key_with_value(self, lst, rules):
        # thus deleting the key
        for key, value in lst:
            for rkey, rvalues in rules.items():
                rules[rkey] = [rv.replace(key, value) for rv in rvalues]
            del rules[key]
        return rules


    def simplify(self, rules):
        cont = True
        # find substitutions.

        # key is the parent of value
        remove_value = []

        # value is the parent of key
        remove_key = []

        for key, values in rules.items():

            # ignore disjoints for now.
            if len(values) != 1:
                continue
            value = values[0]

            # ignore literals and $_START
            if not self.extract_fn(value) or not self.extract_fn(key):
                continue

            if self.is_parent(key, value):
                # choose the parent.
                remove_value.append((key, value))
            elif self.is_parent(value, key):
                remove_key.append((key, value))
            elif key.count('.') > value.count('.'):
                remove_key.append((key, value))
            elif key.count('.') < value.count('.'):
                remove_value.append((key, value))
            else:
                pass

        rules = self.replace_def_of_key_with_value_def(remove_value, rules)
        rules = self.replace_use_of_key_with_value(remove_key, rules)

        return rules
