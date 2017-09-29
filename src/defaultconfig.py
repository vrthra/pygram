extra_verbose = False
check_self = False
check_globals = False
non_trivial = lambda var,val: len(var) >= 1 and len(val) >= 2
in_scope = lambda fn: True
include_ast = False
