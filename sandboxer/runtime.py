import importlib

class Scope(object):
    def __init__(self):
        self.vars = {}

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
        if name in self.vars:
            return self.vars[name]
        raise NameError(name)

    def __setitem__(self, name, value):
        self.vars[name] = value



# Fill scope (usually scope0) with default variables
def populateScope(scope):
    import exceptions
    for name in vars(exceptions):
        scope[name] = getattr(exceptions, name)