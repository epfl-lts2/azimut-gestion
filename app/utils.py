class DjangoLock:

    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(filename, 'w')

    # flock() is a blocking call unless it is bitwise ORed with LOCK_NB to avoid blocking
    # on lock acquisition.  This blocking is what I use to provide atomicity across forked
    # Django processes since native python locks and semaphores only work at the thread level
    def acquire(self):
        import fcntl
        fcntl.flock(self.handle, fcntl.LOCK_EX)

    def release(self):
        import fcntl
        fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __del__(self):
        self.handle.close()
