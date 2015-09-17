"""Contains the class that controls a remote host.

This host object should be a simple wrapper around ssh/scp with a easy, simple
interface. Commands should be able to be executed synchronously or
asynchronously.
"""

from pyrem.task import SubprocessTask

class Host(object):

    def __init__(self, hostname):
        self.__hostname = hostname

    def run(self, command, quiet=False):
        """Run a command on the remote host.

        Args:
            command: Either a string or a list. The command to execute on the
                remote host.
            quiet: Boolean. Whether or not to print process output.
        Return:
            A SubprocessTask.
        """
        if isinstance(command, list):
            command = ' '.join(command)
        return SubprocessTask(['ssh', self.__hostname, command], quiet=quiet)

    def send_file(self, file_name, remote_destination=None, quiet=False):
        if not remote_destination:
            remote_destination = file_name

        return SubprocessTask(
            ['rsync', '-ut', file_name,
             '%s:%s' % (self.__hostname, remote_destination)],
            quiet=quiet)

    def get_file(self, file_name, local_destination=None, quiet=False):
        if not local_destination:
            local_destination = file_name

        return SubprocessTask(
            ['rsync', '-ut', '%s:%s' % (self.__hostname, file_name),
             local_destination],
            quiet=quiet)
