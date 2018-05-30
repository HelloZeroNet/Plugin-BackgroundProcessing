import ast

class Sandboxer(object):
    def __init__(self, code, ext):
        self.code = code
        self.ext = ext
        self.parsed = ast.parse(code, filename="0background.%s" % ext)


    def toSafe(self):
        filename = "0background.%s" % self.ext
        def do():
            exec compile(self.parsed, filename=filename, mode="exec") in {}
        return do