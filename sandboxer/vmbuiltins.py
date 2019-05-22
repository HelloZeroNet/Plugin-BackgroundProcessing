class BuiltinNone(object):
    pass

old_super = super

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
        file = kwargs.get("file", None)
        if file is None:
            # Communication with hosting process
            scope0.io["output"](*args)
        else:
            import builtins
            getattr(builtins, "print")(*args, **kwargs)

    scope0.inherits["print"] = print_

    # input() and raw_input()
    def input_(prompt=None):
        return scope0.io["input"](prompt)

    scope0.inherits["input"] = input_
    scope0.inherits["raw_input"] = input_

    # Attributes
    def getattr_(obj, name):
        return scope0.safeAttr(obj)[name]
    scope0.inherits["getattr"] = getattr_

    def setattr_(obj, name, value):
        scope0.safeAttr(obj)[name] = value
    scope0.inherits["setattr"] = setattr_

    # super
    def super(*args):
        if args == ():
            import sys
            frame = sys._getframe(1)
            self_name = frame.f_code.co_varnames[0]  # usually "self"
            self = frame.f_locals[self_name]
            return old_super(type(self), self)
        else:
            return old_super(*args)
    scope0.inherits["super"] = super

    #arr = ['open', 'compile', '__import__', 'file', 'execfile', 'eval']