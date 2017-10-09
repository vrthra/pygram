"""
The tracer module. It keeps track of the variables created at each point in
the execution
"""
from typing import Dict, Tuple, Any, Optional, List

import sys
import collections
import json
import inspect

from induce.helpers import my_copy, flatten, scrub, decorate
import induce.TEvents

# pylint: disable=multiple-statements,fixme, unidiomatic-typecheck
# pylint: line-too-long

# TODO: Figure out how globals fits into this.
# Globals are like self in that it may also be considered an input.
# However, if there is a shadowing local variable, we should ignore
# the global.


class Tracer:
    """
    Tracer class for tracing the execution of functions and their parameters
    """
    class_cache = {}  # type: Dict[Any, str]

    def __init__(self,
                 in_data: str,
                 out_data: Optional[List[Dict[str, Any]]] = None) -> None:
        self.method = self.tracer()
        self.indata = in_data
        self.outdata = out_data
        self.myvars_stack = []  # type: List[Any]

    def __enter__(self) -> None:
        """ set hook """
        event = [('event', induce.TEvents.Start), ('$input', self.indata)]
        self.out(collections.OrderedDict(event))
        sys.settrace(self.method)

    def __exit__(self, typ: str, value: str, backtrace: Any) -> None:
        """ unhook """
        sys.settrace(None)
        self.out({'event': induce.TEvents.Stop})

    def out(self, val: Dict[str, Any]) -> None:
        """Handle data output either as print or as json string"""
        if self.outdata is not None:
            self.outdata.append(val)
        else:
            print(json.dumps(val), file=sys.stderr)

    def tracer(self) -> Any:
        """ Generates the trace function that gets hooked in.  """

        def loc(caller: Any) -> Tuple[str, str, int]:
            """ Returns location information of the caller """
            return (caller.f_code.co_name, caller.f_code.co_filename,
                    caller.f_lineno)

        def traceit(frame: Any, event: str, arg: Optional[str]) -> Any:
            """ The actual trace function """
            (mname, mfile, mline) = loc(frame)
            self.process_frame(frame, (mfile, str(mline), mname), event, arg)
            return traceit

        return traceit

    def on_call(self, frame: Any,
                _arg: Optional[str]) -> collections.OrderedDict:
        """
        Handle event method call
        """
        frame_env = collections.OrderedDict()  # type: collections.OrderedDict
        frame_env['event'] = induce.TEvents.Enter
        frame_env['stack'] = Tracer.get_stack(frame)

        my_locals_cpy = my_copy(frame.f_locals)
        param_names = [
            frame.f_code.co_varnames[i]
            for i in range(frame.f_code.co_argcount)
        ]
        my_parameters = {
            k: v
            for k, v in my_locals_cpy.items() if k in param_names
        }
        my_variables = {
            k: v
            for k, v in my_locals_cpy.items() if k not in param_names
        }

        # There should be no variables on call.
        assert not my_variables

        frame_env['parameters'] = scrub(flatten(my_parameters))
        frame_env['variables'] = scrub(flatten(my_variables))

        myvars = collections.OrderedDict(
            frame_env['parameters'])  # type: collections.OrderedDict
        self.myvars_stack.append(myvars)

        return frame_env

    def on_return(self, _frame: Any,
                  arg: Optional[str]) -> collections.OrderedDict:
        """
        Handle event method return
        """
        frame_env = collections.OrderedDict()  # type: collections.OrderedDict
        frame_env['event'] = induce.TEvents.Exit
        frame_env['arg'] = scrub(flatten({'<return>': arg}))
        self.myvars_stack.pop()
        return frame_env

    def on_line(self, frame: Any,
                _arg: Optional[str]) -> collections.OrderedDict:
        """
        Handle event line (execution of a single statement)
        """
        frame_env = collections.OrderedDict()  # type: collections.OrderedDict
        frame_env['event'] = induce.TEvents.Line

        frame_env['variables'] = []

        my_locals_cpy = scrub(flatten(my_copy(frame.f_locals)))
        myvars = self.myvars_stack[-1]
        for key, value in my_locals_cpy:
            if myvars.get(key) != value:
                myvars[key] = value
                frame_env['variables'].append((key, value))

        return frame_env

    def process_frame(self, frame: Any, loc: Tuple[str, str, str], event: str,
                      arg: Optional[str]) -> None:
        """
        Process the frame event, and distribute it correctly to
        different event handlers.
        """
        # dont process if the frame is tracer
        # this happens at the end of trace -- Tracer.__exit__
        vself = frame.f_locals.get('self')
        if type(vself) == Tracer: return

        frame_env = None
        if event == 'call':
            frame_env = self.on_call(frame, arg)

        elif event == 'return':
            frame_env = self.on_return(frame, arg)

        elif event == 'line':
            frame_env = self.on_line(frame, arg)

        else:
            raise Exception(event)

        frame_env['loc'] = loc
        self.out(frame_env)

    @classmethod
    def set_cache(cls, code: Any, clazz: str) -> str:
        """ Set the global class cache """
        cls.class_cache[code] = clazz
        return clazz

    @classmethod
    def get_class(cls, frame: Any) -> Optional[str]:
        """ Set the class name"""
        code = frame.f_code
        name = code.co_name
        if cls.class_cache.get(code): return cls.class_cache[code]
        args, _, _, local_dict = inspect.getargvalues(frame)
        class_name = ''

        if name == '__new__':  # also for all class methods
            class_name = local_dict[args[0]].__name__
            return class_name
        try:
            class_name = local_dict['self'].__class__.__name__
            if class_name: return class_name
        except (KeyError, AttributeError):
            pass

        # investigate __qualname__ for class objects.
        for objname, obj in frame.f_globals.items():
            try:
                if obj.__dict__[name].__code__ is code:
                    return cls.set_cache(code, objname)
            except (KeyError, AttributeError):
                pass
            try:
                if obj.__slot__[name].__code__ is code:
                    return cls.set_cache(code, objname)
            except (KeyError, AttributeError):
                pass
        return "@"

    @classmethod
    def get_qualified_name(cls, frame: Any) -> str:
        """ Set the qualified method name"""
        code = frame.f_code
        name = code.co_name  # type: str
        clazz = cls.get_class(frame)
        if clazz: return decorate(clazz, name)
        return name

    @classmethod
    def get_stack(cls, frame: Any) -> List[Tuple[str, int]]:
        """ Get the stack of current call """
        return [(Tracer.get_qualified_name(i[0]), i[0].__hash__())
                for i in reversed(inspect.getouterframes(frame))]
