"""host.py: Contains classes for managing remote hosts.

The ``Host`` object is a simple wrapper around various sorts of Tasks.
"""

__author__ = "Ellis Michael"
__email__ = "emichael@cs.washington.edu"


import platform

from pyrem.task import SubprocessTask, RemoteTask

class Host(object):
    """Abstract class, an object representing some host.

    Attributes:
        hostname (str): The name of the host.
    """
    def __init__(self, hostname):
        self.hostname = hostname

    def run(self, command, **kwargs):
        """Build a task to run the command on a remote host.

        Args:
            command (list of str): The command to execute.

            **kwargs: Keyword args to be passed to the underlying ``Task``'s
                init method.

        Returns:
            ``pyrem.task.Task``: The resulting task.
        """
        raise NotImplementedError


class RemoteHost(Host):
    """A remote host.

    Args:
        hostname (str): The hostname of the remote host.
    """
    def __init__(self, hostname):
        super(RemoteHost, self).__init__(hostname)

    def run(self, command, **kwargs):
        """Run a command on the remote host.

        This is just a wrapper around ``RemoteTask(self.hostname, ...)``
        """
        return RemoteTask(self.hostname, command, **kwargs)

    def send_file(self, file_name, remote_destination=None, **kwargs):
        """Send a file to a remote host with rsync.

        Args:
            file_name (str): The relative location of the file on the local
                host.

            remote_destination (str): The destination for the file on the remote
                host. If `None`, will be assumed to be the same as
                **file_name**. Default `None`.

            **kwargs: Passed to ``SubprocessTask``'s init method.

        Return:
            ``pyrem.task.SubprocessTask``: The resulting task.
        """
        if not remote_destination:
            remote_destination = file_name

        return SubprocessTask(
            ['rsync', '-ut', file_name,
             '%s:%s' % (self.hostname, remote_destination)],
            **kwargs)

    def get_file(self, file_name, local_destination=None, **kwargs):
        """Get a file from a remote host with rsync.

        Args:
            file_name (str): The relative location of the file on the remote
                host.

            local_destination (str): The destination for the file on the local
                host. If `None`, will be assumed to be the same as
                **file_name**. Default `None`.

            **kwargs: Passed to ``SubprocessTask``'s init method.

        Return:
            ``pyrem.task.SubprocessTask``: The resulting task.
        """
        if not local_destination:
            local_destination = file_name

        return SubprocessTask(
            ['rsync', '-ut', '%s:%s' % (self.hostname, file_name),
             local_destination],
            **kwargs)


class LocalHost(Host):
    """The local host."""
    def __init__(self):
        super(LocalHost, self).__init__(platform.node())

    def run(self, command, **kwargs):
        return SubprocessTask(command, **kwargs)

    def move_file(self, file_name, destination, **kwargs):
        """Move a file on the local host.

        Args:
            file_name (str): The relative location of the file.

            destination (str): The relative destination of the file.

            **kwargs: Passed to ``SubprocessTask``'s init method.

        Return:
            ``pyrem.task.SubprocessTask``: The resulting task.
        """
        return SubprocessTask(['mv', file_name, destination], **kwargs)
