"""
Helper module
"""
import sys
import copy
from typing import List, Tuple, Any, Dict, Union
import traceback

# pylint: disable=C0321,R0903,fixme

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
    return [(k, v) for k, v in obj if isinstance(v, str)]

def expand(key: str, value: str, level: int) -> List[Tuple[str, str]]:
    """ Expand one level.  """
    if level <= 0: return [(key, value)]
    if isinstance(value, (dict, list)):
        return [("%s_%s" % (key, k), v) for k, v in flatten(value, level-1)]
    return [(key, value)]

def flatten(val: Union[Dict[(str, Any)], List[Any]], level: int = 10) -> List[Any]:
    """
    Make a nested data structure (only lists and dicts) into a flattened
    dict.
    """
    if isinstance(val, dict): return flatten_dict(val, level)
    elif isinstance(val, list): return flatten_list(val, level)
    return val

def flatten_dict(val: Dict[(str, Any)], level: int) -> List[Any]:
    """ Make a nested dict into a flattened list."""
    lst = []
    for k in val.keys():
        try:
            lst.extend(expand(k, val[k], level))
        except KeyError:
            print(traceback.format_exc())
            continue
    return lst

def flatten_list(val: List[Any], level: int) -> List[Any]:
    """ Make a nested list into a flattened list."""
    return [i for k, v in enumerate(val) for i in expand(str(k), v, level)]

def my_copy_list(inds: List[Any], lvl: int) -> List[Any]:
    """Deep copy a list"""
    if lvl <= 0: return []
    try:
        lst = []
        for item in inds:
            if item is None: continue
            lst.append(my_copy(item, lvl-1))
        return lst
    except IndexError:
        print(traceback.format_exc())
        return []

def my_copy_dict(inds: Dict[str, Any], lvl: int) -> Dict[str, Any]:
    """Deep copy a dict"""
    if lvl <= 0: return {}
    try:
        dct = {}
        for k in inds.keys():
            try:
                dct[k] = inds[k]
            except KeyError:
                print(traceback.format_exc())
                continue
        return dct
    except KeyError:
        print(traceback.format_exc())
        return {}

def my_copy(inds: Any, lvl: int = 10) -> Union[Dict[str, Any], List[Any]]:
    """Deep copy"""
    if inds is None: return None
    if isinstance(inds, list):
        return my_copy_list(inds, lvl)
    elif isinstance(inds, dict):
        return my_copy_dict(inds, lvl)
    try:
        return copy.deepcopy(inds)
    except TypeError:
        print(traceback.format_exc())
        return None
