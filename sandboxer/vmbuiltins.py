class BuiltinNone(object):
	pass

def getBuiltins(scope0):
	builtins = {}

	builtins["help"]        = lambda: None
	builtins["copyright"]   = lambda: None
	builtins["credits"]     = lambda: None
	builtins["license"]     = lambda: None

	builtins["__package__"] = "0background"
	builtins["__name__"]    = "0background"
	builtins["__doc__"]     = ""
	builtins["__debug__"]   = False



	return builtins

	#arr = ['input', 'reload', 'exit', 'print', 'globals', 'open', 'quit', 'raw_input', 'compile', '__import__', 'file', 'execfile', 'eval']