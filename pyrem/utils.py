
def synchronized(func):
    """ Synchronization decorator """
    def locked_function(self, *args, **kwargs):
        # TODO: assertions here
        with self._lock:
            return func(self, *args, **kwargs)
    return locked_function
