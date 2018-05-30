import importlib
from scope import Scope


# Fill scope (usually scope0) with default variables
def populateScope(scope):
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



arr = ['help', 'vars', 'copyright', 'input', 'reload', '__package__', 'locals', 'exit', 'print', 'credits', '__name__', 'license', 'globals', 'open', 'quit', '__doc__', 'raw_input', 'compile', '__import__', 'file', 'execfile', 'eval', '__debug__']
print [name for name in arr if name not in funcs]