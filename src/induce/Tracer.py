"""
The tracer module
"""
from typing import Dict, Tuple, Any, Optional, List

import sys
import collections
import json
import linecache
import ast

from induce.helpers import my_copy, flatten, scrub
# pylint: disable=multiple-statements,fixme, unidiomatic-typecheck, line-too-long

# TODO: At least simple data flow (just parsing simple assignments)
# would be useful to restrict the induced grammar.
# i.e if we only have a = b + c, then we could restrict the grammar of
# $A to just $B $C.
# TODO: Figure out how globals fits into this.
# Globals are like self in that it may also be considered an input.
# However, if there is a shadowing local variable, we should ignore
# the global.

def decorate(clazz: str, _: int, key: str) -> str:
    """Add a class and id prefix to a variable"""
    return '%s.%s' % (clazz, key)


class Tracer:
    """ The context manager that manages trace hooking and unhooking. """
    def __init__(self, in_data: str, out_data: Optional[List[Dict[str, Any]]] = None) -> None:
        self.method = self.tracer()
        self.indata = in_data
        self.outdata = out_data

    def __enter__(self) -> None:
        """ set hook """
        sys.settrace(self.method)

    def __exit__(self, typ: str, value: str, backtrace: Any) -> None:
        """ unhook """
        sys.settrace(None)
        # print an empty record to indicate one full invocation.
        self.out({})

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
            return (caller.f_code.co_name, caller.f_code.co_filename, caller.f_lineno)

        def traceit(frame: Any, event: str, arg: Optional[str]) -> Any:
            """ The actual trace function """
            (mname, mfile, mline) = loc(frame)
            (cname, cfile, cline) = loc(frame.f_back)
            code = linecache.getline(mfile, mline)
            kind = 'unknown'
            try:
                mymod = ast.parse(code.strip())
                if isinstance(mymod, ast.Module) and mymod.body:
                    if len(mymod.body) == 1:
                        kind = " ".join([ast.dump(child) for child in mymod.body])
            except SyntaxError: pass

            self.process_frame(frame,
                               {'name':mname, 'file':mfile, 'line': str(mline),
                                'cname': cname, 'cfile': cfile, 'cline': str(cline),
                                'code': code, 'kind': kind}, event, arg)
            return traceit
        return traceit

    def process_frame(self, frame: Any, loc: Dict[(str, str)], event: str, arg: Optional[str]) -> None:
        """
        For the current frame (distinguished by id), save the parameter values,
        and save all the values that each variable takes. Process globals and
        self specially.
        TODO: Also handle dictionaries (like self), list objects, and other
        custom assignamble objects
        """

        # dont process if the frame is tracer
        # this happens at the end of trace -- Tracer.__exit__
        vself = frame.f_locals.get('self')
        if type(vself) == Tracer: return

        frame_env = collections.OrderedDict() # type: collections.OrderedDict

        my_id = frame.__hash__()
        frame_env['id'] = my_id
        frame_env['func_name'] = loc['name']
        frame_env['caller_name'] = loc['cname']

        my_locals_cpy = my_copy(frame.f_locals)
        param_names = [frame.f_code.co_varnames[i] for i in range(frame.f_code.co_argcount)]
        # split parameters and locals
        my_parameters = {k:v for k, v in my_locals_cpy.items() if k in param_names}
        my_locals = {k:v for k, v in my_locals_cpy.items() if k not in param_names}

        frame_env['variables'] = dict(scrub(flatten(my_locals)))
        frame_env['parameters'] = dict(scrub(flatten(my_parameters)))

        # TODO: At some point, we should remove special casing
        # self. It is just another object found as the first parameter
        # should be assigned to as self[clazz_name+obj_id].member = value
        # and other objects should be varname[clazz_name+obj_id].member = value
        frame_env['self'] = {}
        if hasattr(vself, '__dict__') and type(vself.__dict__) == dict:
            clazz = vself.__class__.__name__
            frame_env['self'].update({decorate(clazz, my_id, k):v for (k, v) in
                                      scrub(flatten(vself.__dict__))})
        frame_env['event'] = event
        frame_env['arg'] = dict(scrub(flatten({'@': arg})))
        frame_env['code'] = loc['code']
        frame_env['kind'] = loc['kind']
        frame_env['$input'] = self.indata

        self.out(frame_env)
