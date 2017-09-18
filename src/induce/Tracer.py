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
        self.grammar = g
        self.frameenv = MultiValueDict()
        self.input = i

    def __enter__(self):
        """ set hook """
        # event in ['call', 'line', 'return', 'exception', 'c_call', 'c_return', 'c_exception']
        # The trace function is invoked (with event set to 'call') whenever a
        # new local scope is entered; it should return a reference to a local
        # trace function to be used that scope, or None if the scope shouldn’t
        # be traced.
        # The local trace function should return a reference to itself (or to
        # another function for further tracing in that scope), or None to turn off
        # tracing in that scope.
        sys.settrace(self.method)

    def __exit__(self, type, value, traceback):
        """ unhook """
        sys.settrace(None)
        self.grammar.update(self.frameenv, self.input)

    def add_frame(self, frameid, frame):
        """
        If the frame.id alredy exists, merge this.
        Expect frame.id, frame.func_name, and frame.parameters and frame.self to remain same.
        in the frameenv['variables'] each variable, if it exists already, becomes a disjunction,
        else it becomes a single element set.
        """
        if self.frameenv.get(frameid) == None:
            self.frameenv[frameid] = frame
        else:
            self.frameenv[frameid]['variables'].merge(frame['variables'])
            self.frameenv[frameid]['self'].merge(frame['self'])
            # throw away frameenv[parameters] and frameenv[func_name] because
            # they should be same for the same frameid (useful assert!)
            #TODO: we should handle other dict like objects at some point.

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
        return if type(vself) in == Tracer

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
        frame_env['variables'] = locals_dict.deepcopy()
        # at some point, we may just want to save the assignments directly
        # rather than relying on locals_dict so that we get the ordering of
        # assignment values.
        frame_env['self'] = self.getmembers(vself) if cfg.check_self else {}
        self.add_frame(frame.id(), frame)


    def tracer(self):
        def loc(caller): return (caller.f_code.co_name, caller.f_code.co_filename, caller.f_lineno)

        def traceit(frame, event, arg):
            # we probably only need event == 'return' for now i(return includes block returns)
            # that is, (until we add dataflow)
            if event != 'return' return traceit

            (n, f, l) = loc(frame)
            if not cfg.in_scope(f): return
            if cfg.extra_verbose:
                (cn, cf, cl) = loc(frame.f_back)
                print('%s() %s:%s\n\t%s()<- %s:%s' % (n, f, l, cn, cf, cl))

            self.process_frame(frame, {'name':n, 'file':f, 'line':l})
            return traceit
        return traceit
