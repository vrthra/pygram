import sys
import copy
import collections
import json
import itertools
import inspect
import Ordered
import config as cfg

# TODO: At least simple data flow (just parsing simple assignments)
# would be useful to restrict the induced grammar.
# i.e if we only have a = b + c, then we could restrict the grammar of
# $A to just $B $C.
# TODO: Figure out how globals fits into this.
# Globals are like self in that it may also be considered an input.
# However, if there is a shadowing local variable, we should ignore
# the global.
# TODO: we need to also take care of values assigned in dicts/arrays

def scrub(obj):
    """
    Remove everything except strings.
    """
    if isinstance(obj, dict):
        return {k:v for k,v in [(k,scrub(v)) for (k,v) in obj.iteritems()] if v != None}
    elif isinstance(obj, list):
        return [k for k in [scrub(k) for k in obj] if k != None]
    elif isinstance(obj, str):
        return obj
    else:
        return None

class Tracer(object):
    """ The context manager that manages trace hooking and unhooking. """
    def __init__(self, i):
        self.method = self.tracer()
        self.frameenv = Ordered.MultiValueDict()
        self.input = i

    def __enter__(self):
        """ set hook """
        sys.settrace(self.method)

    def __exit__(self, type, value, traceback):
        """ unhook """
        sys.settrace(None)
        # print an empty record to indicate one full invocation.
        print >> sys.stderr

    def process_frame(self, frame, loc):
        """
        For the current frame (distinguished by id), save the parameter values,
        and save all the values that each variable takes. Process globals and
        self specially.
        TODO: Also handle dictionaries (like self), list objects, and other
        custom assignamble objects
        """
        def only_strings(points): return {k: v for k, v in points.iteritems() if type(v) in [str]}

        # dont process if the frame is tracer
        # this happens at the end of trace -- Tracer.__exit__
        vself  = frame.f_locals.get('self')
        if type(vself) in [Tracer]: return

        frame_env = collections.OrderedDict()

        frame_env['id'] = frame.__hash__()
        frame_env['func_name'] = loc['name']
        my_parameters = {}
        my_locals = frame.f_locals.copy()

        # split parameters and locals
        for i in range(frame.f_code.co_argcount):
           name = frame.f_code.co_varnames[i]
           my_parameters[name] = my_locals[name]
           del my_locals[name]

        frame_env['variables'] = scrub(my_locals)
        frame_env['parameters'] = scrub(my_parameters)

        frame_env['self'] = {}
        if hasattr(vself, '__dict__') and type(vself.__dict__) in [dict]:
            clazz = vself.__class__.__name__
            frame_env['self'].update({'%s.%s' % (clazz, k):v for (k,v) in
                 scrub(vself.__dict__).iteritems()})
        frame_env['event'] = loc['event']

        print >> sys.stderr, json.dumps(frame_env)


    def tracer(self):
        def loc(caller): return (caller.f_code.co_name, caller.f_code.co_filename, caller.f_lineno)

        def traceit(frame, event, arg):
            # if event != 'return': return traceit
            (n, f, l) = loc(frame)
            if cfg.extra_verbose:
                (cn, cf, cl) = loc(frame.f_back)
                print('%s() %s:%s\n\t%s()<- %s:%s' % (n, f, l, cn, cf, cl))

            self.process_frame(frame, {'name':n, 'file':f, 'line':l, 'event':event})
            return traceit
        return traceit
