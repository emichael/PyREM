"""utils.py: Contains useful utilities to be used in other modules."""

__author__ = "Ellis Michael"
__email__ = "emichael@cs.washington.edu"


import sys

from IPython.terminal.embed import InteractiveShellEmbed


def synchronized(func):
    """Decorator to make function synchronized on self._lock.

    If the first argument to the function (hopefully self) does not have a _lock
    attribute, then this decorator does nothing.
    """
    def locked_function(*args, **kwargs):
        """Apply func inside _lock if it exists."""
        if not (args and hasattr(args[0], '_lock')):
            return func(*args, **kwargs)
        with args[0]._lock: # pylint: disable=W0212
            return func(*args, **kwargs)
    return locked_function

interact = InteractiveShellEmbed(
    banner1="---Starting Interactive Shell---\n",
    exit_msg="---Resuming Program---\n")

# TODO: util for capturing stdout and TEEing it to a file (either concat or overwrite)

CURRENT_TEE = None

class Tee(object):
    def __init__(self, filename, mode):
        self.file = open(filename, mode)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
    def __del__(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.file.close()
    def write(self, data):
        self.file.write(data)
        self.file.flush()
        self.stdout.write(data)

def log_output(filename, mode='w'):
    stop_log_output()
    global CURRENT_TEE
    CURRENT_TEE = Tee(filename, mode)

def stop_log_output():
    global CURRENT_TEE
    if CURRENT_TEE:
        del CURRENT_TEE
    CURRENT_TEE = None
