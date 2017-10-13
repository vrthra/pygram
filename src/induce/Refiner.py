"""
Grammar Refiner module
"""

from typing import List, Any
import sys
import collections
import re
from induce.Rule import RKey, RVal, RFactory
from induce.Ordered import OrderedSet, merge_odicts

def djs_to_string(djs: OrderedSet) -> str:
    """Convert disjoint set to string"""
    return "\n\t| ".join([i.replace('\n', '\n|\t') for i in sorted(djs)])

def grammar_lst(rules: collections.OrderedDict) -> List[str]:
    """
    Convert a given set of rules to their string representation
    """
    def fixline(key, rules):
        fmt = "%s ::= %s" if len(rules) == 1 else "%s ::=\n\t| %s"
        return fmt % (key, djs_to_string(rules))
    return [fixline(key, rules[key]) for key in rules.keys()]

class Refiner:
    """
    Refine gramamr
    """
    def __init__(self) -> None:
        """ Initialize refiner with grammar """
        self.my_grammar = collections.OrderedDict() # type: collections.OrderedDict
        self.max_nth = {}
        self.defined_in = {}
        self.key_tracker = RFactory()

    def update(self, rules: List[Any], key_tracker, ptree):
        """ Add new rules from an invocation"""
        self.parent_tree = ptree # TODO: merge this too.
        self.key_tracker.merge(key_tracker)
        for rkey, rval in rules:
            self.my_grammar.setdefault(rkey, OrderedSet()).add(rval.rule())

    def __str__(self) -> str:
        grammar = self.my_grammar
        # grammar = self.remove_redundant_values(grammar) # -- suspect
        grammar = self.remove_redundant_keys(grammar)
        grammar = self.clean(grammar)
        return "\n".join(grammar_lst(grammar))

    def is_parent(self, parent, child):
        if not child: return False
        parents = self.parent_tree.get(child, set())
        seen = set(parents)
        while parents:
            if parent in parents: return True
            grand_parents = set()
            for new_p in parents:
                gp = self.parent_tree.get(new_p, set()) - seen
                grand_parents |= gp
                seen |= gp
            parents = grand_parents
        return False

    def delete_key(self, key, rules):
        # deleting a key means first replacing the key's defs
        # in each of the rules, and lastly
        # deleting the key's def in the rule
        new_rules = collections.OrderedDict()
        values = rules[key]

        for rkey, rvalues in rules.items():
            if rkey == key: continue
            new_rvalues = OrderedSet()
            for rvalue in rvalues:
                if key in rvalue:
                    for val in values:
                        new_rvalues.append(replace_str_value(rvalue, key, val))
                else:
                    new_rvalues.append(rvalue)
            new_rules[rkey] = new_rvalues

        return new_rvalues

    def replace_in_all_rules(self, rules, kstr1, kstr2):
        str1 = str(kstr1)
        str2 = str(kstr2)
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
        deleted_keys = {}

        for key, value in lst:
            rval = self.key_tracker.parse_key(value)
            while key in deleted_keys:
                key = deleted_keys[key]
            rules[key] = rules[rval]
            del rules[rval]
            # removed value by replacing it with key
            deleted_keys[value] = str(key)

            rules = self.replace_in_all_rules(rules, value, key)

        return rules

    def replace_use_of_key_with_new_key(self, lst, rules):
        # so, delete $my_key1 key, and replace any use of
        # $my_key1 in other rules with $my_key2
        remove_dict = {k:v for k,v in lst}
        for key1, key2 in lst:
            del rules[key1]

        for key1, key2 in lst:
            print(": ", key1, '=>', key2)
            while key2 in remove_dict: key2 = remove_dict[key2]
            print(": ", key1, '..=>', key2)
            rules = self.replace_in_all_rules(rules, key1, key2)
        return rules

    def maxnth(self, key):
        return self.key_tracker.maxnth(key)

    def definedin(self, key):
        return self.key_tracker.defs(key)

    def remove_redundant_values(self, rules):
        # find substitutions.
        remove_value = []  # key is the parent of value
        seen = set()

        for key, values in rules.items():
            # ignore disjoints for now.
            if len(values) != 1:
                continue
            value = values[0]
            if value in seen: continue
            seen.add(value)
            # not a variable.
            pval = self.key_tracker.parse_key(value)
            if not pval: continue

            # ignore literals and $_START
            if not pval.fn or not key.fn:
                continue

            # prefer variables in parent functions over child variables
            if self.is_parent(key.fn, pval.fn):
                remove_value.append((key, value))

            # prefer unnested variables over deeply nested variables
            elif key.fn.count('.') < pval.fn.count('.'):
                remove_value.append((key, value))

            # prefer less often reused variables over variables that are reassigned frequently
            elif self.maxnth(key) < self.maxnth(pval):
                remove_value.append((key, value))

            else:
                pass

        return self.replace_def_of_key_with_value_def(remove_value, rules)


    def remove_redundant_keys(self, rules):
        # given a definition such as $my_key1 = $my_key2
        # $my_key1 is redundant, especially if $my_key2 is
        # preferable over $my_key1.
        # so, delete $my_key1 key, and replace any use of
        # $my_key1 in other rules with $my_key2
        remove_key = []  # value is the parent of key

        for key, values in rules.items():
            # ignore disjoints for now.
            if len(values) != 1:
                continue
            value = values[0]
            pval = self.key_tracker.parse_key(value)
            # not a variable.
            if not pval: continue

            # ignore literals and $_START
            if not pval.fn or not key.fn:
                continue

            # prefer variables in parent functions over child variables
            if self.is_parent(pval.fn, key.fn):
                remove_key.append((key, pval))

            # prefer unnested variables over deeply nested variables
            elif key.fn.count('.') > pval.fn.count('.'):
                remove_key.append((key, pval))

            # prefer less often reused variables over variables that are reassigned frequently
            elif self.maxnth(key) > self.maxnth(pval):
                remove_key.append((key, pval))

            # same var names. Prefer first defined.
            elif key.var == pval.var:
                remove_key.append((key, pval))

            else:
                pass

        return self.replace_use_of_key_with_new_key(remove_key, rules)

    def mk_rkey(self, key, defs) -> str:
        """ return the non-terminal """
        nth_s = ":%s" % key.nth if self.maxnth(key) > 0 else ""
        tail = "[%s,%s]" % (key.fn, key.pos) if len(defs[key.var]) > 1 else ""
        return "$%s%s%s" % (key.var, nth_s, tail)


    def clean(self, rules):
        defs = {}
        for key in rules.keys():
            if key.var in defs:
                defs[key.var].add(key.fn)
            else:
                defs[key.var] = {key.fn}
        rmaps = {key: self.mk_rkey(key, defs) for key in rules.keys()}

        new_rules = rules
        for key, new_key in rmaps.items():
            new_rules = self.replace_key(new_rules, key, new_key)
        return new_rules
