"""
Grammar inference module
"""
# pylint: disable=C0321,fixme, too-few-public-methods,unused-import
from typing import Dict, Any, Iterator, List, Tuple

import collections
import induce.TEvents
import induce.Refiner
from induce.helpers import decorate


def non_trivial_val(val: str) -> bool:
    """ Is the variable temporary? """
    return len(val) >= 2

def mk_nt(val: str) -> str:
    """ return the non-terminal """
    return '$%s' % val.upper()

class Context:
    """ The context of call """
    def __init__(self, stk: List[Tuple[str, int]], loc: List[str]) -> None:
        self.stack = stk
        self.name, self.fnid = stk[-1]
        # line number is sufficient to distinguish the particular assignment
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
        self.visible_vars = [] # type: List[Any]

        self.collected_rules = []
        self.refiner = refiner
        self.parent_tree = {}

    def is_in_input(self, val: str) -> bool:
        """
        Is the value provided nontrivial, and is in the
        input values being considered?
        """
        if not non_trivial_val(val): return False
        last_input = self.input_stack[-1]
        for ikey, ival in last_input:
            if val in ival: return True
        return False

    def add_new_rule(self, key, val):
        added_rule = None
        my_key = self.get_key(key)
        for idx, (rkey, rval) in enumerate(self.collected_rules):
            new_rval = rval
            start = 0
            # replace each occurrence as a new rule.
            # this gives us more fail safety against accidental
            # replacements.
            while start != -1:
                start = rval.find(val, start)
                if start != -1:
                    new_rval = "%s%s%s" % (rval[:start], my_key, rval[start + len(val):])
                    added_rule = (my_key, val)
                    start += 1
            self.collected_rules[idx] = (rkey, new_rval)
        if added_rule: return [added_rule]
        return []


    def get_single_assign_vars(self, variables):
        new_variables = []
        visible_vars = self.visible_vars[-1]
        for key, val in variables:
            if not non_trivial_val(val): continue
            vval = visible_vars.get(key)
            if vval:
                visible_vars[key] = vval + 1
                new_variables.append((decorate(key, str(vval+1), ':'), val))
            else:
                visible_vars[key] = 1
                new_variables.append((key, val))
        return new_variables

    def on_enter(self, frameenv: Dict[str, Any]) -> None:
        """On method call"""
        context = Context(frameenv['context'], frameenv['loc'])
        if self.context_stack:
            last_method = self.context_stack[-1].name
            this_method = context.name
            self.parent_tree.setdefault(this_method, set()).add(last_method)
        self.context_stack.append(context)
        my_parameters = [(k, v) for k, v in frameenv['parameters']]

        self.input_stack.append(my_parameters)
        # starting rules for this method.
        # get the parameters that are non-trivial
        rules = [(key, val) for key, val in my_parameters
                 if self.is_in_input(val)]
        added_rules = []
        for key, val in rules:
            added_rules.extend(self.add_new_rule(key, val))
        self.collected_rules.extend(added_rules)

        self.visible_vars.append({k:0 for k, v in my_parameters})


    def on_exit(self, _frameenv: Dict[str, Any]) -> None:
        """On method call"""
        self.input_stack.pop()
        self.visible_vars.pop()
        self.context_stack.pop()

    def get_key(self, key):
        context = self.context_stack[-1]
        nt_key = mk_nt(key)
        ckey = context.key()
        return "%s[%s,%s]" % (nt_key, ckey[0], ckey[1])

    def on_line(self, frameenv: Dict[str, Any]) -> None:
        """On method call"""
        # the new variables
        my_variables = self.get_single_assign_vars(frameenv['variables'])

        if not my_variables: return
        # now, replace value of each variable in the grammar rules

        added_rules = []
        for key, val in my_variables:
            added_rules.extend(self.add_new_rule(key, val))
        # perform extension separately because variables in new assignments
        # never interact with each other
        self.collected_rules.extend(added_rules)

    def trace_start(self, frameenv: Dict[str, Any]) -> None:
        """Save input at the start of a record"""
        my_input = ('$_START', frameenv['$input'])
        self.input_stack.append([my_input])
        self.collected_rules.append(my_input)

    def trace_stop(self) -> None:
        """ reset grammar at the end of a record"""
        self.refiner.tree(self.parent_tree)
        self.refiner.add_rules(self.collected_rules)
        self.collected_rules = []
        self.input_stack = []

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

