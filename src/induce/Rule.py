import re
import collections

from induce.Ordered import OrderedSet

def qualname(fn, var):
    return "%s:%s" % (fn, var)

class RKey:
    max_nth = collections.defaultdict(int)
    """The variable key"""
    def __init__(self, var, fn, pos, nth=0):
        """ Directly called only for _start"""
        self.var = var
        self.fn = fn
        self.pos = pos
        self.nth = nth
        self.qualname = qualname(fn, var)
        max_nth = RKey.max_nth.get(self.qualname, 0)
        if max_nth > nth:
            RKey.max_nth[self.qualname] = max_nth

    def from_context(var, context):
        fn = context.name
        pos = context.pos
        qn = qualname(fn, var)
        if qualname(fn, var) in RKey.max_nth:
            return RKey(var, fn, pos, RKey.max_nth[qn]+1)
        else:
            return RKey(var, fn, pos, 0)

    def parts(mystr):
        val = re.search('^\$<([^:]+):([0-9]+)>\[(.+),([0-9]+)\]$', mystr)
        if val:
            return {'var':val.group(1), 'nth':int(val.group(2)),
                    'fn':val.group(3), 'pos':val.group(4)}

        val = re.search('^\$<(.+)>\[(.+),([0-9]+)\]$', mystr)
        if val:
            return {'var':val.group(1), 'nth':0,
                    'fn':val.group(2), 'pos':val.group(3)}
        return None


    def from_key(key):
        parts = RKey.parts(key)
        if not parts: return None
        return RKey(parts['var'], parts['fn'], parts['pos'], parts['nth'])

    def is_var(key):
        return re.search('^\$<[^$]+>$', key)

    def maxnth(self):
        return RKey.max_nth[self.qualname]

    def mk_nt(val: str, nth: int = 0) -> str:
        """ return the non-terminal """
        return '$<%s:%s>' % (val, nth)

    def mk_simplent(val: str) -> str:
        """ return the non-terminal """
        return '$%s' % val

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

class RVal:
    def __init__(self, var):
        self.var = var
        self.choices = OrderedSet()

    def add_choice(self, key, val):
        self.choices.add((key, val))

    def contains(self, mystr):
        return mystr in self.var

    def rule(self):
        var = self.var
        for k, v in self.choices:
            # var = "%s>%s:%s" % (var, k, v)
            var = var.replace(v, str(k))
        return var
