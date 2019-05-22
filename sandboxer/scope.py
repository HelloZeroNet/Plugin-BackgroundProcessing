allowed_classes = [
    # Exceptions
    ArithmeticError, AssertionError, AttributeError, BaseException,
    BlockingIOError, BrokenPipeError, BufferError, BytesWarning,
    ChildProcessError, ConnectionAbortedError, ConnectionError,
    ConnectionRefusedError, ConnectionResetError, DeprecationWarning, EOFError,
    EnvironmentError, Exception, FileExistsError, FileNotFoundError,
    FloatingPointError, FutureWarning, GeneratorExit, IOError, ImportError,
    ImportWarning, IndentationError, IndexError, InterruptedError,
    IsADirectoryError, KeyError, KeyboardInterrupt, LookupError, MemoryError,
    ModuleNotFoundError, NameError, NotADirectoryError, NotImplementedError,
    OSError, OverflowError, PendingDeprecationWarning, PermissionError,
    ProcessLookupError, RecursionError, ReferenceError, ResourceWarning,
    RuntimeError, RuntimeWarning, StopAsyncIteration, StopIteration,
    SyntaxError, SyntaxWarning, SystemError, SystemExit, TabError, TimeoutError,
    TypeError, UnboundLocalError, UnicodeDecodeError, UnicodeEncodeError,
    UnicodeError, UnicodeTranslateError, UnicodeWarning, UserWarning,
    ValueError, Warning, ZeroDivisionError,

    # Primitives
    bool, float, int, bytes, str, complex,

    # Objects
    bytearray, dict, frozenset, list, memoryview, object, set, slice, tuple,

    # Transformations
    filter, map, enumerate, zip, reversed,

    # Other
    classmethod, property, range, staticmethod, type, type(None),
    type(NotImplemented), type(Ellipsis), type({}.keys()), type({}.values()),
    type({}.items())
]


class Scope(object):
    def __init__(self, inherits=None, io=None):
        self.vars = {}
        self.inheritsVariable = {}
        self.inherits = inherits
        if inherits is None:
            self.to_close = []
            self.filename = None  # will be set by spawner
            self.io = io
        else:
            self.to_close = inherits.to_close
            self.filename = inherits.filename
            self.io = inherits.io

    def import_(self, names, from_, level):
        if level is not None and level > 0:
            # Import local file
            file_parts = self.filename.split("/")
            if level > len(file_parts):
                if from_ is None:
                    from_ = "."
                raise ImportError("Import of %s outside site root" % from_)

            if from_ is None:
                from_ = []
            else:
                from_ = from_.split(".")
            new_path = "/".join(file_parts[:-level] + from_)

            if new_path not in self.io["import_cache"]:
                # Handle modules
                code, new_path = self.io["readModule"](new_path)
                if code is None:
                    raise ImportError("Cannot read %s" % new_path)

                # Execute code
                from . import Sandboxer
                sandboxer = Sandboxer(code, new_path, io=self.io)
                safe_code = sandboxer.toSafe()
                self.io["import_cache"] = safe_code()


            result_scope = self.io["import_cache"]

            # Import the result
            for name, asname in names:
                if asname is None:
                    asname = name
                if name not in result_scope:
                    raise ImportError("Cannot import %s from %s" % (name, new_path))
                self[asname] = result_scope[name]

            return


        for name, asname in names:
            if asname is None:
                asname = name

            if from_ is not None:
                if from_ not in self.io["allowed_import"]:
                    raise ImportError("%s is not allowed to be imported" % from_)

                scope = {}
                exec(compile("from %s import %s as import_module" % (from_, name), "<import>", "single"), scope, scope)
                import_module = scope["import_module"]
            elif name in self.io["modules"]:
                import_module = self.io["modules"][name](self.io)
                if hasattr(self.io["modules"][name], "close"):
                    self.to_close.append(self.io["modules"][name].close)
            else:
                if name not in self.io["allowed_import"]:
                    raise ImportError("%s is not allowed to be imported" % name)

                scope = {}
                exec(compile("import %s as import_module" % name, "<import>", "single"), scope, scope)
                import_module = scope["import_module"]

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

    def __contains__(self, name):
        try:
            self[name]
            return True
        except NameError:
            return False

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
        for name, value in dct.items():
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
        elif name in ("__globals__", "func_globals"):
            return self["globals"]()
        elif name in ("__code__", "func_code"):
            raise TypeError("%s is unsafe" % name)

        return getattr(self.obj, name)

    def __setitem__(self, name, value):
        if name == "__subclasses__":
            raise TypeError("__subclasses__ is read-only")
        elif name == "__globals__":
            raise TypeError("__globals__ is read-only")
        elif name in ("__code__", "func_code"):
            raise TypeError("%s is unsafe" % name)

        setattr(self.obj, name, value)