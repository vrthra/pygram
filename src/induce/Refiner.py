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
    def fix(key, rules):
        if len(rules) == 1:
            return "%s ::= %s" % (key, djs_to_string(rules))
        else:
            return "%s ::=\n\t| %s" % (key, djs_to_string(rules))
    return [fix(key, rules[key]) for key in rules.keys()]

Parts = collections.namedtuple('Parts', ['uvar', 'var', 'nth', 'fn', 'line'])

class Refiner:
    """
    Refine gramamr
    """
    def __init__(self) -> None:
        """ Initialize refiner with grammar """
        self.my_grammar = collections.OrderedDict() # type: collections.OrderedDict
        self.max_use_uvar = {}

    def add_rules(self, rules: List[Any]):
        """ Add new rules from an invocation"""
        for rkey, rval in rules:
            self.my_grammar.setdefault(rkey, OrderedSet()).add(rval)

    def tree(self, ptree):
        self.parent_tree = ptree

    def __str__(self) -> str:
        grammar = self.my_grammar
        grammar = self.update_vars(grammar)
        grammar = self.remove_redundant_values(grammar)
        grammar = self.remove_redundant_keys(grammar)
        grammar = self.clean(grammar) 
        return "\n".join(grammar_lst(grammar))

    def is_parent(self, parent, child):
        if not child: return False
        nxt_step = self.parent_tree.get(child)
        while nxt_step:
            if parent in nxt_step: return True
            new_step = set()
            for i in nxt_step:
                v = self.parent_tree.get(i)
                if v: new_step |= v
            nxt_step = new_step
        return False

    def parts(self, mystr):
        val = re.search('^([^:]+):([0-9]+)\[(.+),([0-9]+)\]$', mystr)
        if val:
            return Parts(uvar = val.group(1), var="%s:%s" % (val.group(1), val.group(2)), nth=int(val.group(2)), fn=val.group(3), line=val.group(4))

        val = re.search('^(.+)\[(.+),([0-9]+)\]$', mystr)
        if val:
            return Parts(uvar = val.group(1), var=val.group(1), nth=0, fn=val.group(2), line=val.group(3))

        val = re.search('^(.+)$', mystr)
        if val:
            return Parts(uvar = val.group(1), var=val.group(1), nth=0, fn='@', line='')
        return Parts(uvar=None, var=None, nth=None, fn=None, line=None)

    def replace_in_all_rules(self, rules, str1, str2):
        new_rules = collections.OrderedDict()
        for key, values in rules.items():
            new_values = OrderedSet()
            for value in values:
                new_value = value.replace(str1, str2)
                new_values.add(new_value)
            new_rules[key] = new_values
        return new_rules

    def replace_key(self, rules, key1, key2):
        new_rules = collections.OrderedDict()
        for key, values in rules.items():
            if key == key1:
                new_rules[key2] = values
            else:
                new_rules[key] = values
        return self.replace_in_all_rules(new_rules, key1, key2)

    def replace_def_of_key_with_value_def(self, lst, rules):
        # thus deleting the value
        kvdict = dict(lst)
        rkvdict = dict({v:k for (k,v) in lst})

        for key, value in lst:
            rules[key] = rules[value]
            del rules[value]

        for key, value in lst:
            while True:
                # can we use the key? is it already replaced?
                if rkvdict.get(key):
                    key = rkvdict[key]
                else:
                    break
            rules = self.replace_in_all_rules(rules, value, key)

        return rules

    def replace_use_of_key_with_value(self, lst, rules):
        kvdict = dict(lst)
        rkvdict = dict({v:k for (k,v) in lst})
        # thus deleting the key
        for key, value in lst:
            del rules[key]

        for key, value in lst:
            while True:
                # can we use the key? is it already replaced?
                if kvdict.get(value):
                    value = kvdict[value]
                else:
                    break
            rules = self.replace_in_all_rules(rules, key, value)
        return rules

    def update_vars(self, rules):
        for key in rules.keys():
            pkey = self.parts(key)
            if self.max_use_uvar.get(pkey.uvar, 0) < pkey.nth:
                self.max_use_uvar[pkey.uvar] = pkey.nth

        keymap = {}
        new_rules = collections.OrderedDict()
        for key in rules.keys():
            pkey = self.parts(key)
            if pkey.nth == 0 and self.max_use_uvar.get(pkey.uvar, 0) > 0:
                new_key = '%s:0[%s,%s]' % (pkey.uvar, pkey.fn, pkey.line)
                keymap[key] = new_key
                new_rules[new_key] = rules[key]
            else:
                new_rules[key] = rules[key]

        for key, new_key in keymap.items():
            new_rules = self.replace_in_all_rules(new_rules, key, new_key)
        return new_rules

    def remove_redundant_values(self, rules):
        # find substitutions.
        remove_value = []  # key is the parent of value

        for key, values in rules.items():
            # ignore disjoints for now.
            if len(values) != 1:
                continue
            value = values[0]

            pkey = self.parts(key)
            pval = self.parts(value)

            # ignore literals and $_START
            if not pval.fn or not pkey.fn:
                continue

            # prefer variables in parent functions over child variables
            if self.is_parent(pkey.fn, pval.fn):
                remove_value.append((key, value))

            # prefer unnested variables over deeply nested variables
            elif pkey.fn.count('.') < pval.fn.count('.'):
                remove_value.append((key, value))

            # prefer less often reused variables over variables that are reassigned frequently
            elif self.max_use_uvar.get(pkey.uvar, 0) < self.max_use_uvar.get(pval.uvar, 0):
                remove_value.append((key, value))

            else:
                pass

        return self.replace_def_of_key_with_value_def(remove_value, rules)


    def remove_redundant_keys(self, rules):
        # find substitutions.
        remove_key = []  # value is the parent of key

        for key, values in rules.items():
            # ignore disjoints for now.
            if len(values) != 1:
                continue
            value = values[0]

            pkey = self.parts(key)
            pval = self.parts(value)

            # ignore literals and $_START
            if not pval.fn or not pkey.fn:
                continue

            # prefer variables in parent functions over child variables
            if self.is_parent(pval.fn, pkey.fn):
                remove_key.append((key, value))

            # prefer unnested variables over deeply nested variables
            elif pkey.fn.count('.') > pval.fn.count('.'):
                remove_key.append((key, value))

            # prefer less often reused variables over variables that are reassigned frequently
            elif self.max_use_uvar.get(pkey.uvar, 0) > self.max_use_uvar.get(pval.uvar, 0):
                remove_key.append((key, value))

            else:
                pass

        return self.replace_use_of_key_with_value(remove_key, rules)

    def clean(self, rules):
        maps = {}
        rmaps = {}
        new_rules = rules
        for key in rules.keys():
            pkey = self.parts(key)
            new_key = pkey.var
            if not new_key or maps.get(new_key):
                new_key = key
            maps[new_key] = key
            rmaps[key] = new_key

        for key, new_key in rmaps.items():
            new_rules = self.replace_key(new_rules, key, new_key)
        return new_rules


