from Plugin import PluginManager

@PluginManager.registerTo("UiWebsocket")
class UiWebsocketPlugin(object):
	def actionRestartBackgroundScripts(self, to):
		if "BACKGROUND" in self.site.settings["permissions"]:
			# Stop threads
			self.site.spawner.stopAll()
			# Start them
			self.site.spawned_background_processes = False
			self.site.spawnBackgroundProcesses()
			# Reply
			self.response(to, "ok")
		else:
			self.response(to, {"error": "No BACKGROUND permission"})