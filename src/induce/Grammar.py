"""
Grammar inference module
"""
# pylint: disable=C0321,fixme, too-few-public-methods,unused-import
from typing import Dict, Any, Iterator, List

from contextlib import contextmanager
import collections
import induce.TEvents
from induce.helpers import decorate


def non_trivial_val(val: str) -> bool:
    """ Is the variable temporary? """
    return len(val) >= 2

def non_term(val: str) -> str:
    """ return the non-terminal """
    return '$%s' % val.upper()

class Context:
    """ The context of call """
    def __init__(self, stk: Any) -> None:
        self.stack = stk
        self.name, self.fnid = stk[-1]
        self.strrep = decorate(self.name, self.fnid, ':')

    def __str__(self) -> str:
        """ the string representation """
        return self.strrep


class Grammar:
    """
    Grammar inference
    """
    TRACE_START = 1
    TRACE_STOP = 0
    TRACE_CONT = -1

    def __init__(self) -> None:
        """ Initialize grammar """
        self.call_stack = [] # type: List[Any]
        self.input_stack = [] # type: List[Any]
        self.context_stack = [] # type: List[Any]
        self.visible_vars = [] # type: List[Any]

    def is_in_input(self, val: str) -> bool:
        """
        Is the value provided nontrivial, and is in the
        input values being considered?
        """
        last_input = self.input_stack[-1]
        return non_trivial_val(val) and (val in last_input)


    def on_enter(self, frameenv: Dict[str, Any]) -> None:
        """On method call"""
        self.context_stack.append(Context(frameenv['stack']))
        print("> ", str(self.context_stack[-1]))
        # get the parameters that are non-trivial
        my_parameters = [(k, v) for k, v in frameenv['parameters']
                         if self.is_in_input(v)]

        # starting rules for this method.
        rules = [((non_term(key), val)) for key, val in my_parameters]
        self.call_stack.append(rules)
        self.visible_vars.append({k:0 for k, v in my_parameters})


    def on_exit(self, _frameenv: Dict[str, Any]) -> None:
        """On method call"""
        rules = self.call_stack.pop()
        self.visible_vars.pop()
        print("< ", str(self.context_stack.pop()))
        for key, val in rules:
            print(key, "::=", val)

    def on_line(self, frameenv: Dict[str, Any]) -> None:
        """On method call"""
        visible_vars = self.visible_vars[-1]
        rules = self.call_stack[-1]
        # the new variables
        new_variables = []
        for key, val in frameenv['variables']:
            if not non_trivial_val(val): continue
            vval = visible_vars.get(key)
            if vval:
                visible_vars[key] = vval + 1
                new_variables.append((decorate(key, str(vval+1), ':'), val))
            else:
                visible_vars[key] = 1
                new_variables.append((key, val))

        if not new_variables: return
        # now, replace value of each variable in the grammar rules

        added_rules = []
        for key, val in new_variables:
            nt_key = non_term(key)
            for idx, (rkey, rval) in enumerate(rules):
                new_rval = rval
                # replace each occurrence as a new rule.
                # this gives us more fail safty against accidental
                # replacements.
                while True:
                    # replace the first occurrence
                    if val in new_rval:
                        new_rval = new_rval.replace(val, nt_key, 1)
                        added_rules.append((nt_key, val))
                    elif val.upper() in new_rval:
                        new_rval = new_rval.replace(val.upper(), nt_key, 1)
                        added_rules.append((nt_key, val.upper()))
                    elif val.lower() in new_rval:
                        new_rval = new_rval.replace(val.lower(), nt_key, 1)
                        added_rules.append((nt_key, val.lower()))
                    else:
                        break
                    rules[idx] = (rkey, new_rval)

        rules.extend(added_rules)
        self.call_stack[-1] = rules


    def trace_start(self, frameenv: Dict[str, Any]) -> None:
        """Save input at the start of a record"""
        self.input_stack.append(frameenv['$input'])

    def trace_stop(self) -> None:
        """ reset grammar at the end of a record"""

    def handle_events(self, jframe: Dict[str, Any]) -> int:
        """Calll correct events based on the frame"""
        event = jframe['event']
        if  event == induce.TEvents.Start:
            self.trace_start(jframe)
            return Grammar.TRACE_START
        if event == induce.TEvents.Stop:
            self.trace_stop()
            return Grammar.TRACE_STOP

        myframe = collections.OrderedDict(sorted(jframe.items(), key=lambda x: x[0]))
        if event == induce.TEvents.Enter:
            self.on_enter(myframe)
        elif event == induce.TEvents.Exit:
            self.on_exit(myframe)
        elif event == induce.TEvents.Line:
            self.on_line(myframe)
        return Grammar.TRACE_CONT

@contextmanager
def grammar(hide: bool = False) -> Iterator[Any]:
    """The context manager for grammar"""
    mygrammar = Grammar()
    yield mygrammar
    lines = "_" * 80
    if not hide: print(("%s\n%s\n%s" % (lines, mygrammar, lines)))
