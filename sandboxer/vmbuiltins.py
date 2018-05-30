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

    def globals():
        return scope0["locals"]()
    scope0.inherits["globals"] = globals

    def reload():
        raise NotImplementedError("reload() is not supported")
    scope0.inherits["reload"] = reload

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

    #arr = ['input', 'print', 'open', 'raw_input', 'compile', '__import__', 'file', 'execfile', 'eval']