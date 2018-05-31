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
                if from_ not in self.io.allowed_import:
                    raise ImportError("%s is not allowed to be imported" % from_)

                exec compile("from %s import %s as import_module" % (from_, name), "<import>", "single")
            elif name in self.io.modules:
                import_module = self.io.modules[name](self.io)
            else:
                if name not in self.io.allowed_import:
                    raise ImportError("%s is not allowed to be imported" % name)

                exec compile("import %s as import_module" % name, "<import>", "single")

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


    def safeGet(self, obj, name):
        if name == "__subclasses__":
            def subclasses():
                return [
                    subclass for subclass
                    in obj.__subclasses__()
                    if subclass in allowed_classes
                ]

            return subclasses
        elif name in ("__globals__", "func_globals"):
            return self["globals"]()
        elif name in ("__code__", "func_code"):
            raise TypeError("%s is unsafe" % name)

        return getattr(obj, name)