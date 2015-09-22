
def synchronized(lock=None):
    """ Synchronization decorator """
    def _(func):
        def locked_function(self, *args, **kwargs):
            if lock:
                with lock:
                    return func(self, *args, **kwargs)
            else:
                with self._lock:
                    return func(self, *args, **kwargs)
        return locked_function
