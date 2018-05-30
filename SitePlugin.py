from Plugin import PluginManager
from spawner import Spawner

@PluginManager.registerTo("Site")
class SitePlugin(object):
    def __init__(self, *args, **kwags):
        super(SitePlugin, self).__init__(*args, **kwags)

        # Now spawn background process if needed
        self.spawner = Spawner(self)
        self.spawned_background_processes = False
        if "BACKGROUND" in self.settings["permissions"]:
            self.spawnBackgroundProcesses()


    def spawnBackgroundProcesses(self):
        if self.spawned_background_processes:
            return

        self.log.debug("Spawning background processes")
        self.spawned_background_processes = True
        files = self.storage.list("")
        for file in files:
            # Run every file that starts with 0background.
            if file.startswith("0background."):
                self.spawnBackgroundProcess(file)


    # Spawn background process if needed
    def spawnBackgroundProcess(self, file_name):
        ext = file_name.replace("0background.", "")
        # Read code
        code = self.storage.read(file_name)
        # Spawn
        self.spawner.spawn(ext, code)



    def delete(self):
        # First really delete
        super(SitePlugin, self).delete(self)
        # Now stop all threads
        self.spawner.stopAll()