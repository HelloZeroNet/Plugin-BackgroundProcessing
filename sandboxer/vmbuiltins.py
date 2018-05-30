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

	#arr = ['input', 'print', 'open', 'raw_input', 'compile', '__import__', 'file', 'execfile', 'eval']