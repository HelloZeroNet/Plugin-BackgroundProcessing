import gevent
import logging
import os
import importlib
from sandboxer import Sandboxer

class Spawner(object):
    def __init__(self, site, io):
        self.site = site
        self.log = logging.getLogger("Spawner:%s" % self.site.address_short)
        self.threads = []
        self.io = io


    def spawn(self, ext, code):
        # Find correct transpiler for this file, based on extension
        transpiler = self.findTranspiler(ext)
        if transpiler is None:
            self.log.debug("No transpiler for 0background.%s" % ext)
            return False

        # Transpile
        self.log.debug("Transpiling 0background.%s" % ext)
        try:
            transpiled = transpiler.transpile(code)
        except Exception, e:
            self.log.exception("Error transpiling 0background.%s" % ext)
            return False

        # Sandbox
        sandboxer = Sandboxer(code, ext, io=self.io)
        safe_code = sandboxer.toSafe()

        self.log.debug("Running 0background.%s" % ext)
        self.threads.append((ext, safe_code()))


    def findTranspiler(self, ext):
        try:
            return importlib.import_module("BackgroundProcessing.transpilers.%s" % ext)
        except ImportError:
            try:
                return importlib.import_module("transpilers.%s" % ext)
            except ImportError:
                return None


    # Stop all threads
    def stopAll(self):
        for scope0 in self.io["scope0"]:
            for f in scope0.to_close:
                f(self.io)
        for _, thread in self.threads:
            thread.kill(block=False)
        self.threads = []
        self.io["scope0"] = []

    # Stop by extension
    def stop(self, ext):
        new_threads = []
        for ext1, thread in self.threads:
            if ext == ext1:
                thread.kill(block=False)
        self.threads = [thread for thread in self.threads if thread[0] != ext]