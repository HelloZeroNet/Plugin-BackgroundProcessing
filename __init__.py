import BackgroundPlugin
import SitePlugin
import storage

def addModule(name, module):
	storage.modules[name] = module

# Add ZeroFrame module
import zeroframe
addModule("ZeroFrame", zeroframe.module)