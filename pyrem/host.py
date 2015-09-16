"""Contains the class that controls a remote host.

This host object should be a simple wrapper around ssh/scp with a easy, simple
interface. Commands should be able to be executed synchronously or
asynchronously.
"""

import os

from subprocess import Popen


DEVNULL = file(os.devnull)


class Host(object):

    def __init__(self, hostname):
        self.__hostname = hostname
        self.__waiting_on = set() # set of Popen

    def _exec(self, command, wait, quiet):
        args = {}
        if quiet:
            args['stdin'] = DEVNULL
            args['stdout'] = DEVNULL
            args['stderr'] = DEVNULL

        process = Popen(command, **args) # pylint: disable=W0142
        if wait:
            process.wait()
        else:
            self.__waiting_on.add(process)

    def run(self, command, wait=True, quiet=False):
        """Run a command on the remote host.

        Eventually, this and the other two functions should return a Task object
        that can be interacted with just like any other Task.

        Args:
            command: Either a string or a list. The command to execute on the
                remote host.

            wait: Boolean. Whether or not to wait for the command to finish on
                the remote host. Default True.
        """
        if isinstance(command, list):
            command = ' '.join(command)
        self._exec(['ssh', self.__hostname, command], wait, quiet)

    def send_file(self, file_name, remote_destination=None, wait=True, quiet=False):
        if not remote_destination:
            remote_destination = file_name

        self._exec(['rsync', '-ut', file_name,
                    '%s:%s' % (self.__hostname, remote_destination)], wait, quiet)

    def get_file(self, file_name, local_destination=None, wait=True, quiet=False):
        self._exec(['rsync', '-ut', '%s:%s' % (self.__hostname, file_name),
                    local_destination], wait, quiet)

    def wait_all(self):
        for process in self.__waiting_on:
            process.wait()
        self.__waiting_on = set()
