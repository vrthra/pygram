import sys
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

    def add_if_found(self, var, value):
        """ if the value of the variable was found in the input, add it to the current environment"""
        if value in self.input: self.grammar.add_env(var, value)

    def sel_vars(self, env):
        """ get only string variables (for now). """
        return [(k,v) for (k,v) in env.items() if type(v) == str]

    def getmembers(self, obj):
        """ get member attributes of a self variable """
        if obj == None or not hasattr(obj, '__dict__'): return {}
        n = type(obj).__name__
        return { "%s:%s" % (n, v):v for (k,v)  in vars(obj)}


    def process_frame(self, frame):
        """
        Does nothing but get all the var=value pairs from the current environment. Various
        configuration options control which scopes are checked.
        """
        # dont process if the frame is tracer
        # this happens at the end of trace -- Tracer.__exit__
        vself  = frame.f_locals.get('self')
        if type(vself) in [Tracer]: return

        env = frame.f_globals.copy() if cfg.check_globals else {}
        env.update(frame.f_locals) # the globals are shadowed.
        env.update(self.getmembers(vself) if cfg.check_self else {})

        for var, value in self.sel_vars(env): self.add_if_found(var, value)

    def tracer(self):
        def info(caller): return (caller.f_lineno, caller.f_code.co_filename, caller.f_code.co_name)

        def traceit(frame, event, arg):
            (l, f, n) = info(frame)
            if not cfg.in_scope(f): return
            if cfg.extra_verbose:
                (cl, cf, cn) = info(frame.f_back)
                print('%s() %s:%s\n\t%s()<- %s:%s' % (n, f, l, cn, cf, cl))

            self.process_frame(frame)
            return traceit
        return traceit
