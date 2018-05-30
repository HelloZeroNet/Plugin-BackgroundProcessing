import gevent
import logging
import os
import importlib

class Spawner(object):
    def __init__(self, site):
        self.site = site
        self.log = logging.getLogger("Spawner:%s" % self.site.address_short)
        self.threads = []


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
        safe_code = self.sandbox(code)

        self.threads.append(gevent.spawn(self, safe_code))


    def findTranspiler(self, ext):
        try:
            return importlib.import_module("transpilers.%s" % ext)
        except ImportError, e:
            return None

    def sandbox(self, code):
        raise NotImplementedError


    # Stop all threads
    def stopAll(self):
        for thread in self.threads:
            thread.kill(block=False)
        self.threads = []