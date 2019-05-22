import gevent

def module(io):
    class Util:
        def sleep(self, sec):
            gevent.sleep(sec)
        def parallel(self, f):
            io["spawner"].threads.append(gevent.spawn(f))

    return Util()