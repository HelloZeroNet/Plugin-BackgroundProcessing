_cache = {}

def module(io):
	if io["site"].address in _cache:
		return _cache[io["site"].address]


	import sys
	import gevent
	from User import UserManager
	from Ui import UiWebsocket

	# Create a fake WebSocket
	class WS(object):
		def send(self, *args, **kwargs):
			pass
	ws = WS()

	# Create a fake UiRequest
	class FakeUiRequest(object):
		def __init__(self):
			self.env = {
				"REMOTE_ADDR": "0.0.0.0"
			}
		def getWrapperNonce(self):
			return ""
	ui_request = FakeUiRequest()

	# Create fake UiWebsocket
	waiting_ids = {}
	class FakeUiWebsocket(UiWebsocket):
		# Responses
		def response(self, to, result):
			if to in waiting_ids:
				waiting_ids[to].set_result(result)

		# Callbacks
		def cmd(self, cmd, params={}, cb=None):
			attr_name = "on" + cmd[0].upper() + cmd[1:]
			if hasattr(zeroframe, attr_name):
				getattr(zeroframe, attr_name)(params)

	site = io["site"]
	user = UserManager.user_manager.get()

	# Create a fake UiWebsocket
	ui_server = sys.modules["main"].ui_server

	ui_websocket = FakeUiWebsocket(ws, site, ui_server, user, ui_request)
	site.websockets.append(ui_websocket)  # Add to site websockets to allow notify on events

	last_req_id = [0]

	class ZeroFrame(object):
		def cmd(self, cmd, *args, **kwargs):
			wait = kwargs.pop("wait", False)

			# Check params
			if len(args) == 0:
				params = kwargs
			elif len(kwargs) == 0:
				params = list(args)
			else:
				raise TypeError("ZeroFrame.cmd() accepts either *vararg or **kwarg, not both")

			# Generate ID
			req_id = last_req_id[0]
			last_req_id[0] += 1

			if wait:
				# Set callback
				waiting_ids[req_id] = gevent.event.AsyncResult()

			# Send
			ui_websocket.handleRequest({
				"cmd": cmd,
				"params": params,
				"id": req_id
			})

			if wait:
				# Wait
				result = waiting_ids[req_id].get()

				# Reply
				del waiting_ids[req_id]
				if isinstance(result, dict) and "error" in result:
					raise ValueError(result["error"])
				else:
					return result

		# Same as settings .on... attribute, but can set several handlers
		def on(self, event_name, func):
			attr_name = "on" + event_name[0].upper() + event_name[1:]
			old_handler = getattr(self, attr_name, None)
			def handler(*args, **kwargs):
				if old_handler is not None:
					try:
						old_handler(*args, **kwargs)
					except:
						pass
				func(*args, **kwargs)
			setattr(self, attr_name, handler)

		# A simplier way to call API, e.g.:
		# ZeroFrame.fileGet("content.json")
		def __getattr__(self, name):
			def call(*args, **kwargs):
				return self.cmd(name, *args, **kwargs)
			return call

	zeroframe = ZeroFrame()
	_cache[io["site"].address] = zeroframe
	return zeroframe

def close(io):
	zeroframe = _cache[io["site"].address]
	for key in list(zeroframe.__dict__.keys()):
		if key.startswith("on"):
			delattr(zeroframe, key)
module.close = close