"""
Helper module
"""
import sys
import re
from typing import List, Tuple, Any, Dict
import traceback

MAX_COPY = 10

# pylint: disable=multiple-statements,too-few-public-methods,fixme, unidiomatic-typecheck

def slurp(src: str) -> str:
    """ read a file completely """
    with open(src) as myfile:
        return myfile.read()

def slurpl(src: str) -> List[str]:
    """ read a file completely, and split lines """
    return slurp(src).split('\n')

def slurplstrip(src: str) -> List[str]:
    """ read a file completely, and split lines and strip them """
    return [line.strip() for line in slurpl(src)]


def slurparg() -> str:
    """ use first argument """
    return slurp(sys.argv[1])

def slurplarg() -> List[str]:
    """ use first argument """
    return slurpl(sys.argv[1])

def slurplstriparg() -> List[str]:
    """ use first argument """
    return slurplstrip(sys.argv[1])


def scrub(obj: List[Tuple[str, Any]]) -> List[Tuple[str, str]]:
    """ Remove everything except strings from a flattened datastructure. """
    return sorted([(k, v) for k, v in obj if isinstance(v, str)], key=lambda x: x[0])

def expand(key: str, value: Any, lvl: int) -> List[Tuple[str, str]]:
    """ Expand one level."""
    if lvl <= 0: return [(key, value)]
    if type(value) in [dict, list, tuple]:
        return [(decorate(key, k), v) for k, v in flatten(value, lvl-1)]
    return [(key, value)]

def flatten(val: Any, lvl: int = MAX_COPY) -> Any:
    """
    Make a nested data structure (only lists and dicts) into a flattened
    dict.
    """
    if type(val) == dict: return flatten_dict(val, lvl)
    elif type(val) == list: return flatten_list(val, lvl)
    elif type(val) == tuple: return flatten_tuple(val, lvl)
    return val

def flatten_dict(vals: Dict[(str, Any)], lvl: int) -> List[Any]:
    """ Make a nested dict into a flattened list."""
    return [i for key, val in vals.items()
            for i in expand(key, val, lvl)]

def flatten_tuple(vals: Tuple, lvl: int) -> List[Any]:
    """Make a nested list into a flattened list."""
    return [i for key, val in enumerate(vals)
            for i in expand(str(key), val, lvl)]

def flatten_list(vals: List[Any], lvl: int) -> List[Any]:
    """Make a nested list into a flattened list."""
    return [i for key, val in enumerate(vals)
            for i in expand(str(key), val, lvl)]

def my_copy_list(inds: List[Any], lvl: int) -> List[Any]:
    """Deep copy a list"""
    if lvl <= 0: return []
    try:
        return [my_copy(val, lvl - 1) for val in inds]
    except IndexError:
        print(traceback.format_exc())
        raise

def my_copy_dict(inds: Dict[str, Any], lvl: int) -> Dict[str, Any]:
    """Deep copy a dict"""
    if lvl <= 0: return {}
    try:
        return {key:my_copy(val, lvl - 1) for key, val in inds.items()}
        # ideally KeyError never should happen. However, if we
        # use instanceof(obj,dict) and the obj is a class that
        # inherits from dict, there is no guarantee that a key
        # visible in the keyset is actually accessible.
    except KeyError:
        print(traceback.format_exc())
        raise

def my_copy(inds: Any, lvl: int = MAX_COPY) -> Any:
    """Deep copy. We flush out the datastructures, expanding any cyclical
    and other back references upto lvl. This helps us later in scrub and flatten
    where we have some guarantee of no errors until this depth."""
    if inds is None: return None
    # Do not do isinstance here. The custom dict derived classes such as
    # http-parser.IOrderedDict which do not guarantee the inviolability of
    # the dict behavior can bite us.
    if type(inds) == list:
        return my_copy_list(inds, lvl)
    elif type(inds) == dict:
        return my_copy_dict(inds, lvl)
    try:
        # we dont care what happens to other ds for now.
        return inds
    except TypeError:
        return None
    except (KeyError, IndexError): # See the violation of dict guarantee
        return None

def decorate(stem: str, key: str, sep: str = '.') -> str:
    """Prepend a prefix to key"""
    return '%s%s%s' % (stem, sep, key)

SUBS = '_'
def varsubs(var):
    """Replace any variable by SUBS character"""
    def myrepl(matchobj):
        l = len(matchobj.group(0))
        return SUBS * l
    p = '\$<[^<>]+>\[[^\[\]]+\]'
    val = re.sub(p, myrepl, var)
    return val

def replace_str_value(my_str, val, rep):
    replaced = False
    new_str = my_str
    start = 0
    while start != -1:
        start = varsubs(new_str).find(val, start)
        if start != -1:
            new_str = "%s%s%s" % (new_str[:start], rep, new_str[start + len(val):])
            replaced = True
            start += 1
    return (replaced, new_str)


def get_best(rval):
    max_rep = 0
    min_vars = float('inf')
    best = list(rval)[0]
    for k in rval:
        replaced = varsubs(k)
        replaced_len = replaced.count(Grammar.SUBS)
        var_len = k.count('$')
        # first look for maximum number of replacements.
        # then look for minimum number of '$' used to accomplish it
        if replaced_len > max_rep:
            max_rep = replaced_len
            min_vars = var_len
            best = k
        elif replaced_len == max_rep and var_len < min_vars:
            min_vars = var_len
            best = k

    return {best}
