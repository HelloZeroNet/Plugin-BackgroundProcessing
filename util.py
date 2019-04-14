import gevent

def module(io):
	class Util:
		def sleep(self, sec):
			gevent.sleep(sec)

	return Util()