class BuiltinNone(object):
	pass

def setBuiltins(scope0):
	scope0["help"]        = lambda: None
	scope0["copyright"]   = lambda: None
	scope0["credits"]     = lambda: None
	scope0["license"]     = lambda: None

	scope0["__package__"] = "0background"
	scope0["__name__"]    = "0background"
	scope0["__doc__"]     = ""
	scope0["__debug__"]   = False

	#arr = ['input', 'reload', 'exit', 'print', 'globals', 'open', 'quit', 'raw_input', 'compile', '__import__', 'file', 'execfile', 'eval']