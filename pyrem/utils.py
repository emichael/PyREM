"""utils.py: Contains useful utilities to be used in other modules."""

__author__ = "Ellis Michael"
__email__ = "emichael@cs.washington.edu"


from decorator import decorator

@decorator
def synchronized(func, *args, **kwargs):
    """Function decorator to make function synchronized on ``self._lock``.

    If the first argument to the function (hopefully self) does not have a _lock
    attribute, then this decorator does nothing.
    """
    if not (args and hasattr(args[0], '_lock')):
        return func(*args, **kwargs)
    with args[0]._lock: # pylint: disable=W0212
        return func(*args, **kwargs)
