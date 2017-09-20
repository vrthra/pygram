extra_verbose = False
check_self = False
check_globals = False
non_trivial = lambda var,val: len(var) >= 1 and len(val) >= 2
in_scope = lambda fn: True
decorate = False

# in functions that take a self parameter, it is often the case
# that many members of the self object remain unused. Unless we
# scan and remove unused parameters, on grammar merge, the unused
# self objects combines with the same attribute in other functions
# where they are decomposed.
strip_unused_params = False
