import pudb; brk = pudb.set_trace
from tstr import get_t, tstr

Accessed_scop_var = {}
def update_var(var): Accessed_scop_var[var] += 1
def init_var(var):
    if var not in Accessed_scop_var: Accessed_scop_var[var] = 0

class Vars:
    defs = None

    def init(i):
        Vars.defs = {'START':i}

    def base_name(var, frame):
        return "%d:%s:%s" % (frame.f_lineno, frame.f_code.co_name, var)

    def var_name(var, frame):
        bv = Vars.base_name(var, frame)
        t = Accessed_scop_var[bv]
        # DONT use line number. We are called from every line and the line
        # number is the line where a var is used  not where it is defined.
        return "<%s:%s:%d>" % (frame.f_code.co_name, var, t)

    def update_vars(var, value, frame):
        tv = get_t(value)
        if tv and len(tv) > 0 and InputStack.has(tv):
            bv = Vars.base_name(var, frame)
            init_var(bv)
            qual_var = Vars.var_name(var, frame)
            if not Vars.defs.get(qual_var):
                v = get_t(value)
                assert type(v) is tstr
                Vars.defs[qual_var] = v
                print(qual_var, '=', v)
            else: # possible reassignment
                oldv = Vars.defs.get(qual_var)
                newv = get_t(value)
                if oldv._taint != newv._taint:
                    update_var(bv)
                    qual_var = Vars.var_name(var, frame)
                    Vars.defs[qual_var] = newv

def taint_include(gword, gsentence):
    return set(gword._taint) <= set(gsentence._taint)

class InputStack:
    inputs = []

    def has(val):
        return any(taint_include(val, var)
                for var in InputStack.inputs[-1].values())

    def push(inputs):
        my_inputs = {k:get_t(v) for k,v in inputs.items() if get_t(v)}
        if InputStack.inputs:
            my_inputs = {k:v for k,v in my_inputs.items() if InputStack.has(v)}
        InputStack.inputs.append(my_inputs)

    def pop(): return InputStack.inputs.pop()

# We record all string variables and values occurring during execution
def traceit(frame, event, arg):
    if 'tstr.py' in frame.f_code.co_filename: return traceit
    if event == 'call':
        param_names = [frame.f_code.co_varnames[i]
                       for i in range(frame.f_code.co_argcount)]
        my_parameters = {k: v for k, v in frame.f_locals.items()
                         if k in param_names}
        InputStack.push(my_parameters)

        for var, value in my_parameters.items():
            Vars.update_vars(var, value, frame)
        return traceit

    elif event == 'return':
        InputStack.pop()
        return traceit

    elif event == 'exception':
        return traceit

    variables = frame.f_locals
    for var, value in variables.items(): Vars.update_vars(var, value, frame)

    return traceit
