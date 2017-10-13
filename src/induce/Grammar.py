"""
Grammar inference module
"""
# pylint: disable=C0321,fixme, too-few-public-methods,unused-import
from typing import Dict, Any, Iterator, List, Tuple

import collections
import induce.TEvents
import induce.Refiner
from induce.Rule import RKey, RVal, RFactory
from induce.helpers import decorate, replace_str_value
from induce.Ordered import OrderedSet

def non_trivial_val(val: str) -> bool:
    """ Is the variable temporary? """
    return len(val) >= 2

class Context:
    """ The context of call """
    def __init__(self, stk: List[Tuple[str, int]], loc: List[str]) -> None:
        self.stack = stk
        self.name, self.fnid = stk[-1]
        # line number is sufficient to distinguish the particular assignment
        # but not repeated assignments in loops
        self.pos = loc[1]
        self.strrep = decorate(self.name, self.fnid, ':')

    def key(self):
        """ the key for this context """
        return (self.name, self.pos, self.fnid)

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

    def __init__(self, refiner: induce.Refiner) -> None:
        """ Initialize grammar """
        # For keeping track of the parameters
        self.input_stack = [] # type: List[Any]

        # Keeping track of the context information.
        # in the call stack.
        self.context_stack = [] # type: List[Any]

        # The variables currently visible to the method.
        # Used for ensuring that reassignments are tracked.
        self.visible_vars_stack = [] # type: List[Any]

        self.collected_rules = []
        self.refiner = refiner
        self.parent_tree = {}
        self.called_method = None
        self.key_tracker = RFactory()

    def is_in_input(self, val: str) -> bool:
        """
        Is the value provided nontrivial, and is in the
        input values being considered?
        """
        if not non_trivial_val(val): return False
        last_input = self.input_stack[-1]
        return any(val in ival for _ikey, ival in last_input)

    def add_new_rule(self, key, val, base_method):
        def stem(key):
            """The name of the variable, without array/dict extensions"""
            return key.split('.')[0]
        def same_def(key1, key2):
            """ Do not let the part of same nested variables be a choice"""
            val = (key1.fn == key2.fn and
                    key1.pos == key2.pos and
                    stem(key1.var) == stem(key2.var))
            return val
        added_choice = False
        if not self.is_in_input(val): return []

        nkey = self.key_tracker.key_from_context(key, self.current_context())

        for idx, (rkey, rval) in enumerate(self.collected_rules):
            # limit search to one step up and down.
            # TUNABLE
            # if rkey.fn not in base_method: continue
            if rval.contains(val) and not same_def(rkey, nkey):
                rval.add_choice(nkey, val)
                added_choice = True
        if added_choice:
            return [(nkey, RVal(val))]
        return []

    def on_enter(self, frameenv: Dict[str, Any]) -> None:
        """On method call"""

        context = Context(frameenv['context'], frameenv['loc'])
        last_method = self.context_stack[-1].name
        this_method = context.name
        self.parent_tree.setdefault(this_method, set()).add(last_method)

        self.context_stack.append(context)
        my_parameters = frameenv['parameters']

        self.input_stack.append(my_parameters)
        # starting rules for this method.
        added_rules = []
        for key, val in my_parameters:
            added_rules.extend(self.add_new_rule(key, val, {last_method}))
        self.collected_rules.extend(added_rules)

        self.visible_vars_stack.append({k:0 for k, v in my_parameters})

    def on_exit(self, _frameenv: Dict[str, Any]) -> None:
        """On method call"""
        self.input_stack.pop()
        self.visible_vars_stack.pop()
        self.called_method = self.context_stack.pop().name

    def current_context(self):
        return self.context_stack[-1]

    def on_line(self, frameenv: Dict[str, Any]) -> None:
        """On method call"""
        # the new variables
        my_variables = frameenv['variables']
        if not my_variables: return
        # now, replace value of each variable in the grammar rules

        added_rules = []
        for key, val in my_variables:
            rel_methods = {self.current_context().name, self.called_method}
            added_rules.extend(self.add_new_rule(key, val, rel_methods))
        self.called_method = None
        # perform extension separately because variables in new assignments
        # should not interact with each other
        self.collected_rules.extend(added_rules)

    def trace_start(self, frameenv: Dict[str, Any]) -> None:
        """Save input at the start of a record"""
        my_input = ('_START', frameenv['$input'])
        self.input_stack.append([my_input])
        self.collected_rules.append((self.key_tracker.start_rule('_start'), RVal(frameenv['$input'])))
        self.context_stack.append(Context([('@',0)], ('_','0')))

    def trace_stop(self) -> None:
        """ reset grammar at the end of a record"""
        self.refiner.update(self.collected_rules, self.key_tracker, self.parent_tree)
        self.parent_tree = {}
        self.collected_rules = []
        self.input_stack = []
        self.key_tracker = RFactory()

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
