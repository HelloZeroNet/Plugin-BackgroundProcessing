import importlib
from scope import Scope
from vmbuiltins import getBuiltins


# Return scope-before-scope0
def getRootScope():
    scope = {}

    # Exceptions
    import exceptions
    for name in vars(exceptions):
        scope[name] = getattr(exceptions, name)

    # Built-in constants
    scope["False"] = False
    scope["True"] = True
    scope["None"] = None
    scope["NotImplemented"] = NotImplemented
    scope["Ellipsis"] = Ellipsis

    # Types
    types = [
        "bytearray", "unicode", "memoryview", "dict", "list", "set", "bytes",
        "slice", "frozenset", "float", "basestring", "long", "type", "tuple",
        "reversed", "str", "int", "complex", "bool", "buffer", "object",
    ]
    for type_name in types:
        scope[type_name] = eval(type_name)  # Couldn't find a better way

    # Secure default functions
    funcs = [
        "oct", "bin", "format", "repr", "sorted", "iter", "round", "dir", "cmp",
        "reduce", "intern", "issubclass", "sum", "getattr", "abs", "hash",
        "len", "ord", "super", "filter", "range", "staticmethod", "pow",
        "divmod", "enumerate", "apply", "zip", "hex", "next", "chr", "xrange",
        "hasattr", "delattr", "setattr", "property", "coerce", "unichr", "id",
        "min", "any", "map", "max", "callable", "classmethod"
    ]
    for func_name in funcs:
        scope[func_name] = eval(func_name)  # Couldn't find a better way

    # Now add more builtins
    scope.update(getBuiltins(scope))

    return scope