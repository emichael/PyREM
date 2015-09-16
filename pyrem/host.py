"""Contains the class that controls a remote host.

This host object should be a simple wrapper around ssh/scp with a easy, simple
interface. Commands should be able to be executed synchronously or
asynchronously.
"""

from subprocess import Popen


class Host(object):

    def __init__(self, hostname):
        self.__hostname = hostname

    def run(self, command, wait=True):
        """Run a command on the remote host.

        Args:
            command: Either a string or a list. The command to execute on the
                remote host.

            wait: Boolean. Whether or not to wait for the command to finish on
                the remote host. Default True.
        """
        if isinstance(command, list):
            command = ' '.join(command)
        proc = Popen(['ssh', self.__hostname, command], shell=False)
        if wait:
            proc.wait()
