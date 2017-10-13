import re
import collections
import heapq
import itertools

from induce.Ordered import OrderedSet
import induce.helpers

# How many variables to leave out
MAX_DEPTH = 3

def qualname(fn, var):
    return "%s:%s" % (fn, var)


class RFactory:
    def __init__(self):
        self.max_nth = {}
        self.defined_in =  collections.defaultdict(set)

    def update_account(self, rk):
        v = self.defined_in[rk.var]
        v.add((rk.fn, rk.pos))
        max_nth = self.max_nth.get(rk.qualname)
        if not max_nth:
            self.max_nth[rk.qualname] = rk.nth
        else:
            if rk.nth > max_nth:
                self.max_nth[rk.qualname] = rk.nth

    def merge(self, tracker):
        for k,v in tracker.max_nth.items():
            sval = self.max_nth.get(k)
            if not sval or v > sval:
               self.max_nth[k] = v

        for k,v in tracker.defined_in.items():
            self.defined_in[k] |= v

    def key_from_context(self, var, context):
        fn = context.name
        pos = context.pos
        qn = qualname(fn, var)
        rk = None
        if qualname(fn, var) in self.max_nth:
            rk = RKey(var, fn, pos, self.max_nth[qn]+1)
        else:
            rk = RKey(var, fn, pos, 0)
        self.update_account(rk)
        return rk

    def start_rule(self, var):
        """ Only for _start"""
        rk = RKey(var, '@', '0', 0)
        self.update_account(rk)
        return rk

    def parts(mystr):
        val = re.match('^\$<([^: <>]+):([0-9]+)>\[([^ <>]+),([0-9]+)\]$', mystr)
        if val:
            return {'var':val.group(1), 'nth':int(val.group(2)),
                    'fn':val.group(3), 'pos':val.group(4)}

        val = re.match('^\$<([^ <>]+)>\[([^ <>]+),([0-9]+)\]$', mystr)
        if val:
            return {'var':val.group(1), 'nth':0,
                    'fn':val.group(2), 'pos':val.group(3)}
        return None

    def parse_key(self, key):
        parts = RFactory.parts(key)
        if not parts: return None
        # we do not keep track of this. To be called only from refiner
        return RKey(parts['var'], parts['fn'], parts['pos'], parts['nth'])

    def maxnth(self, key):
        return self.max_nth[key.qualname]

    def defs(self, key):
        return self.defined_in.get(key.var)

class RKey:
    """The variable key"""
    def __init__(self, var, fn, pos, nth=0):
        self.var = var
        self.fn = fn
        self.pos = pos
        self.nth = nth
        self.qualname = qualname(fn, var)



    def mk_nt(val: str, nth: int = 0) -> str:
        """ return the non-terminal """
        return '$<%s:%s>' % (val, nth)

    def __str__(self):
        nt_key = RKey.mk_nt(self.var, self.nth)
        return "%s[%s,%s]" % (nt_key, self.fn, self.pos)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if not isinstance(other, self.__class__): return NotImplemented
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Define a non-equality test"""
        if not isinstance(other, self.__class__): return NotImplemented
        return not self.__eq__(other)

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))

def fitness(var):
    val = induce.helpers.varsubs(var)
    orig_len = len(var)
    new_len = len(val.replace(induce.helpers.SUBS, ''))
    return new_len # smaller new_len is better for heapify

def use_all(my_str, choices):
    for key, val in choices:
        my_str = my_str.replace(val, str(key))
    return my_str

def leave_n_out(my_str, choices, n):
    till = len(choices)-n-1
    if till < 0: till = 0
    for num in range(len(choices), till, -1):
        for subset in itertools.combinations(choices, num):
            val = use_all(my_str, subset)
            yield val

class RVal:
    def __init__(self, var):
        self.var = var
        self.choices = OrderedSet()
        self.rstr = None

    def add_choice(self, key, val):
        self.choices.add((key, val))

    def contains(self, mystr):
        return mystr in self.var

    def rule_fitness(self):
        heap = []
        if not self.choices: return self.var

        pos = 0 # ensure that initial variables are preferred over later ones
        for val in leave_n_out(self.var, self.choices, MAX_DEPTH):
            heapq.heappush(heap, (fitness(val), pos, val)) # smallest item
            pos += 1
        return heapq.heappop(heap)[2]

    def rule_simple(self):
        return use_all(self.var, self.choices)

    def rule_debug(self):
        var = self.var
        for k, v in self.choices:
            var = "%s>%s:%s" % (var, str(k), v)
        return var

    def rule(self):
        if not self.rstr:
           self.rstr = self.rule_fitness()
        return self.rstr
