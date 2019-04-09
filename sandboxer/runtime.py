import importlib
import builtins
from .scope import Scope, allowed_classes
from .vmbuiltins import setBuiltins


# Return scope-before-scope0
def fillScope0(scope0):
    scope0.inherits = {}

    # Built-in constants
    scope0.inherits["False"] = False
    scope0.inherits["True"] = True
    scope0.inherits["None"] = None
    scope0.inherits["NotImplemented"] = NotImplemented
    scope0.inherits["Ellipsis"] = Ellipsis

    # Types and exceptions
    for type_object in allowed_classes:
        type_name = type_object.__name__
        if hasattr(builtins, type_name):
            scope0.inherits[type_name] = getattr(builtins, type_name)

    # Secure default functions
    funcs = [
        "abs", "all", "any", "ascii", "bin", "callable", "chr", "delattr",
        "dir", "divmod", "format", "getattr", "hasattr", "hash", "hex", "id",
        "isinstance", "issubclass", "iter", "len", "max", "min", "next", "oct",
        "ord", "pow", "repr", "round", "setattr", "sorted", "sum"
    ]
    for func_name in funcs:
        scope0.inherits[func_name] = getattr(builtins, func_name)

    # Now add more builtins
    setBuiltins(scope0)