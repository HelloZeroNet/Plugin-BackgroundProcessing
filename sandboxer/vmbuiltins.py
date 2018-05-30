class BuiltinNone(object):
    pass

def setBuiltins(scope0):
    scope0.inherits["help"]        = lambda: None
    scope0.inherits["copyright"]   = lambda: None
    scope0.inherits["credits"]     = lambda: None
    scope0.inherits["license"]     = lambda: None

    scope0.inherits["__package__"] = "0background"
    scope0.inherits["__name__"]    = "0background"
    scope0.inherits["__doc__"]     = ""
    scope0.inherits["__debug__"]   = False

    # globals()
    def globals():
        return scope0["locals"]()
    scope0.inherits["globals"] = globals

    # reload()
    def reload():
        raise NotImplementedError("reload() is not supported")
    scope0.inherits["reload"] = reload

    # print and print()
    def print_(*args, **kwargs):
        nl = kwargs["nl"]
        dest = kwargs["dest"]
        if dest is None:
            # Communication with hosting process
            scope0.io["output"](*args)
        else:
            import builtins
            getattr(builtins, "print")(*args, end="\n" if nl else "", file=dest)

    scope0.inherits["print"] = print_

    # input() and raw_input()
    def input_(prompt=None):
        return scope0.io["input"](prompt)

    scope0.inherits["input"] = input_
    scope0.inherits["raw_input"] = input_

    #arr = ['open', 'compile', '__import__', 'file', 'execfile', 'eval']