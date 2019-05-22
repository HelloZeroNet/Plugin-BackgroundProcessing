from Plugin import PluginManager
from .spawner import Spawner
from . import storage

@PluginManager.registerTo("Site")
class SitePlugin(object):
    def __init__(self, *args, **kwags):
        super(SitePlugin, self).__init__(*args, **kwags)

        # Now spawn background process if needed
        io = {
            "output": self.backgroundOutput,
            "input": self.backgroundInput,
            "readModule": self.readModule,
            "allowed_import": (
                "json", "re", "datetime", "base64", "collections", "random"
            ),
            "modules": storage.modules,
            "site": self,
            "scope0": [],
            "import_cache": {}
        }
        self.spawner = Spawner(self, io=io)
        self.spawned_background_processes = False
        if "BACKGROUND" in self.settings["permissions"]:
            self.spawnBackgroundProcesses()

        self.onFileDone.append(self.reloadBackgroundProcess)


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

    # If a background process is changed, reload it
    def reloadBackgroundProcess(self, inner_path):
        if inner_path.startswith("0background."):
            self.spawner.stopAll()
            self.spawnBackgroundProcesses()


    def delete(self):
        # First really delete
        super(SitePlugin, self).delete()
        # Now stop all threads
        self.spawner.stopAll()


    def saveSettings(self):
        super(SitePlugin, self).saveSettings()

        # Spawn if just got the permission
        if "BACKGROUND" in self.settings["permissions"]:
            self.spawnBackgroundProcesses()

    # IO
    def backgroundOutput(self, *args):
        print(*args)
    def backgroundInput(self, *args):
        raise NotImplementedError
    def readModule(self, path):
        if self.storage.isDir(path):
            path += "/__init__.py"
        else:
            path += ".py"

        try:
            with self.storage.open(path, "r") as f:
                return f.read(), path
        except IOError:
            return None, path