import importlib
from scope import Scope
from vmbuiltins import setBuiltins


# Return scope-before-scope0
def fillScope0(scope0):
    scope0.inherits = {}

    # Exceptions
    import exceptions
    for name in vars(exceptions):
        scope0.inherits[name] = getattr(exceptions, name)

    # Built-in constants
    scope0.inherits["False"] = False
    scope0.inherits["True"] = True
    scope0.inherits["None"] = None
    scope0.inherits["NotImplemented"] = NotImplemented
    scope0.inherits["Ellipsis"] = Ellipsis

    # Types
    types = [
        "bytearray", "unicode", "memoryview", "dict", "list", "set", "bytes",
        "slice", "frozenset", "float", "basestring", "long", "type", "tuple",
        "reversed", "str", "int", "complex", "bool", "buffer", "object",
    ]
    for type_name in types:
        scope0.inherits[type_name] = eval(type_name)  # Couldn't find a better way

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
        scope0.inherits[func_name] = eval(func_name)  # Couldn't find a better way

    # Now add more builtins
    setBuiltins(scope0)