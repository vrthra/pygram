import types
import inspect
import functools

def sink(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for e in (list(args) + list(kwargs.values())):
           if isinstance(e, tstr):
              raise Exception("tainted: %s" % e._taint)
        return func(*args, **kwargs)
    return wrapper

def mark(module):
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, types.FunctionType) or isinstance(obj, types.BuiltinFunctionType):
            yield (module, name, obj)


def mark_sinks(module):
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, types.FunctionType) or isinstance(obj, types.BuiltinFunctionType):
            setattr(module, name, sink(obj))

class tstr(str):
    def __radd__(self, other): 
        t =  tstr(str.__add__(other, self))
        t._taint = self._taint
        return t

    def __repr__(self): 
        return self.__class__.__name__ + str.__repr__(self) + " " + str(self.tainted())

    def taint(self):
        self._taint = True
        return self

    def tainted(self):
        if hasattr(self, '_taint'): return "taint:" + str(self._taint)
        else: return "Not tainted"


def make_str_wrapper(fun):
    def proxy(*args, **kwargs):
        res = fun(*args, **kwargs)
    
        if res.__class__ == str:
            t = tstr(res)
            if hasattr(args[0], '_taint'):
               t._taint = args[0]._taint
            return t
        return res
    return proxy

for name, fn in inspect.getmembers(str, callable):
    if name not in ['__class__', '__new__', '__str__', '__init__', '__repr__']:
        setattr(tstr, name, make_str_wrapper(fn))

def source(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return tstr(func(*args, **kwargs)).taint()
    return wrapper

def mark_sources(module):
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, types.FunctionType) or isinstance(obj, types.BuiltinFunctionType):
            setattr(module, name, source(obj))

