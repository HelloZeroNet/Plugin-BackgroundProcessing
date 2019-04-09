from . import BackgroundPlugin
from . import SitePlugin
from . import UiWebsocketPlugin
from . import storage

def addModule(name, module):
	storage.modules[name] = module

# Add ZeroFrame module
from . import zeroframe
addModule("ZeroFrame", zeroframe.module)

# Add Crypt module
from . import crypt
addModule("Crypt", crypt.module)