allowed_classes = [
    type, int, basestring, bytearray, list, type(None), type(NotImplemented),
    super, xrange, dict, set, slice, staticmethod, complex, float, buffer, long,
    frozenset, property, memoryview, tuple, enumerate, reversed, type(Ellipsis),
    classmethod, type({}.iterkeys()), type({}.iteritems()),
    type({}.itervalues())
]


class Scope(object):
    def __init__(self, inherits=None, io=None):
        self.vars = {}
        self.inheritsVariable = {}
        self.inherits = inherits
        self.io = io

    def import_(self, names, from_, level):
        for name, asname in names:
            if asname is None:
                asname = name

            if from_ is not None:
                line = "from %s import %s as import_module" % (from_, name)
            else:
                line = "import %s as import_module" % name

            exec compile(line, "<import>", "single")
            self[asname] = import_module
            del import_module


    def __getitem__(self, name):
        if name in self.inheritsVariable:
            scope = self.inheritsVariable[name]
            return scope[name]
        if name in self.vars:
            return self.vars[name]

        # Vars
        if name == "vars":
            return self.getVars()
        elif name == "locals":
            return self.getLocals()


        if self.inherits is not None:
            if isinstance(self.inherits, Scope):
                return self.inherits[name] # Recursive: type(inherits)==Scope
            elif name in self.inherits:
                return self.inherits[name]

        raise NameError(name)

    def __setitem__(self, name, value):
        if name in self.inheritsVariable:
            scope = self.inheritsVariable[name]
            scope[name] = value
            return

        if isinstance(value, type):
            # User-defined class
            allowed_classes.append(value)

        self.vars[name] = value


    def inherit(self):
        return Scope(self)
    def inheritVariable(self, scope, name):
        self.inheritsVariable[name] = scope

    def extend(self, dct):
        scope1 = Scope(self)
        for name, value in dct.iteritems():
            scope1[name] = value
        return scope1


    def getVars(self):
        class ThisNone(object):
            pass
        def vars(object=ThisNone):
            if object is ThisNone:
                return self["locals"]()
            return object.__dict__
        return vars

    def getLocals(self):
        def locals():
            return self.vars
        return locals


    def safeAttr(self, obj):
        return SafeAttr(obj)


class SafeAttr(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, name):
        if name == "__subclasses__":
            def subclasses():
                return [
                    subclass for subclass
                    in self.obj.__subclasses__()
                    if subclass in allowed_classes
                ]

            return subclasses
        elif name == "__globals__":
            return self["globals"]()
        elif name in ("__code__",):
            raise TypeError("%s is unsafe" % name)

        return getattr(self.obj, name)

    def __setitem__(self, name, value):
        if name == "__subclasses__":
            raise TypeError("__subclasses__ is read-only")
        elif name == "__globals__":
            raise TypeError("__globals__ is read-only")
        elif name in ("__code__",):
            raise TypeError("%s is unsafe" % name)

        setattr(self.obj, name, value)