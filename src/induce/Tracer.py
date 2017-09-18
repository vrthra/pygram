import sys
import copy
import itertools
import inspect
import Grammar
import config as cfg
class Tracer(object):
    """ The context manager that manages trace hooking and unhooking. """
    def __init__(self, i, g):
        self.method = self.tracer()
        self.input, self.grammar = i, g

    def __enter__(self):
        """ set hook """
        sys.settrace(self.method)

    def __exit__(self, type, value, traceback):
        """ unhook """
        sys.settrace(None)
        self.grammar.update(self.input)

    def add_env(self, var, value, loc):
        self.grammar.add_env(var, value, loc)
    
    def add_frame(self, frameid, frame):
        self.grammar.add_frame(frameid, frame)

    def sel_vars(self, env):
        """ get only string variables (for now). """
        return [(k,v) for (k,v) in env.items() if type(v) == str]

    def getmembers(self, obj):
        """ get member attributes of a self variable """
        if obj == None or not hasattr(obj, '__dict__'): return {}
        n = type(obj).__name__
        return { "%s.%s" % (n, v):v for (k,v)  in vars(obj)}

    def decorate(self, decname, name): return decname if cfg.decorate else name

    def process_frame(self, frame, loc):
        """
        For the current frame (distinguished by id), save the parameter values,
        and save all the values that each variable takes. Process globals and
        self specially.
        Also handle dictionaries, list objects, and other custom assignamble objects
        """
        # dont process if the frame is tracer
        # this happens at the end of trace -- Tracer.__exit__
        vself  = frame.f_locals.get('self')
        return if type(vself) in [Tracer, Grammar]

        # TODO: we need to also take care of values assigned in dicts/arrays
        # TODO: also ensure that we save the parameters=value.
        # TODO: Figure out how globals fits into this.

        frame_env = MultiValueDict()
        frame_env['id'] = frame.id()
        frame_env['func_name'] = loc['name']
        args, varargs, varkw, locals_dict = inspect.getargvalues(frame)

        # don't filter anything here. All the filtering will be done later.
        # deep copy because people can modify the parameters.
        frame_env['parameters'] = dict(itertools.chain(args.deepcopy().iteritems(), varargs.deepcopy().iteritems(), varkw.deepcopy().iteritems()))
        frame_env['variables'] = locals_dict
        frame_env['self'] = self.getmembers(vself) if cfg.check_self else {}
        self.add_frame(frame.id(), frame)


    def tracer(self):
        def loc(caller): return (caller.f_code.co_name, caller.f_code.co_filename, caller.f_lineno, caller.id())

        def traceit(frame, event, arg):
            (n, f, l) = loc(frame)
            if not cfg.in_scope(f): return
            if cfg.extra_verbose:
                (cn, cf, cl) = loc(frame.f_back)
                print('%s() %s:%s\n\t%s()<- %s:%s' % (n, f, l, cn, cf, cl))

            self.process_frame(frame, {'name':n, 'file':f, 'line':l})
            return traceit
        return traceit
