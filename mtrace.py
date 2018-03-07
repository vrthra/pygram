from tstr import get_t, tstr

class Vars:
    defs = None

    def init(i):
        Vars.defs = {'START':i}

    def varname(var, frame):
        fn = frame.f_code.co_name
        t = Called_Functions[fn]
        # class_name = frame.f_code.co_name
        # if frame.f_code.co_name == '__new__':
        #   class_name = frame.f_locals[frame.f_code.co_varnames[0]].__name__
        # return "%s:%s" % (class_name, var) # (frame.f_code.co_name, frame.f_lineno, var)
        #return "%s:%s:%s(%d)" % (frame.f_code.co_name, frame.f_lineno, var, n)
        #return "<%s:%s(%d)>" % (frame.f_code.co_name, var, n)
        return "<%d:%s:%s>" % (t, frame.f_code.co_name, var)

    def update_vars(var, value, frame):
        tv = get_t(value)
        if tv and len(tv) > 0 and InputStack.has(tv):
           qual_var = Vars.varname(var, frame)
           if not Vars.defs.get(qual_var):
               v = get_t(value)
               assert type(v) is tstr
               Vars.defs[qual_var] = v
def taint_include(gword, gsentence):
    if set(gword._taint) <= set(gsentence._taint):
        start_i = gsentence._taint.index(gword._taint[0])
        end_i = gsentence._taint.index(gword._taint[-1])
        return (gsentence, start_i, end_i)
    return None

class InputStack:
    # The current input string
    inputs = []

    def has(val):
        return any(taint_include(val, var) for var in InputStack.inputs[-1].values())

    def push(inputs):
        my_inputs = {k:get_t(v) for k,v in inputs.items() if get_t(v)}
        if InputStack.inputs:
            my_inputs = {k:v for k,v in my_inputs.items() if InputStack.has(v)}
        InputStack.inputs.append(my_inputs)

    def pop():
        return InputStack.inputs.pop()

Called_Functions = {}

def register_frame(frame):
    fn = frame.f_code.co_name
    if fn not in Called_Functions:
        Called_Functions[fn] = 0
    Called_Functions[fn] += 1

# We record all string variables and values occurring during execution
def traceit(frame, event, arg):
    if 'tstr.py' in frame.f_code.co_filename: return traceit
    if event == 'call':
        register_frame(frame)

        param_names = [frame.f_code.co_varnames[i]
                       for i in range(frame.f_code.co_argcount)]
        my_parameters = {k: v for k, v in frame.f_locals.items()
                         if k in param_names}
        #print(" |" * (len(InputStack.inputs)+1), ">", frame.f_code.co_name, ':', ','.join(map(str,zip(my_parameters.keys(), my_parameters.values()))))

        InputStack.push(my_parameters)

        for var, value in my_parameters.items():
            Vars.update_vars(var, value, frame)
        return traceit

    elif event == 'return':
        #print(" |" * (len(InputStack.inputs)),"<", frame.f_code.co_name)
        InputStack.pop()
        return traceit

    elif event == 'exception':
        return traceit

    variables = frame.f_locals
    for var, value in variables.items():
        #print(var, value)
        Vars.update_vars(var, value, frame)

    return traceit
