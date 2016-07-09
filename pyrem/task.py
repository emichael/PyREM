"""task.py: Contains the main unit of execution in PyREM, the task."""

__author__ = "Ellis Michael"
__email__ = "emichael@cs.washington.edu"

__all__ = ['Task', 'SubprocessTask', 'RemoteTask', 'Parallel',
           'Sequential']

import atexit
import os
import random
import string
import signal
import sys

from collections import defaultdict
from enum import Enum
from subprocess import Popen, PIPE
from threading import RLock, Thread
from traceback import format_exception

from pyrem.utils import synchronized


TaskStatus = Enum('TaskStatus', 'IDLE STARTED STOPPED') # pylint: disable=C0103

STARTED_TASKS = set()

@atexit.register
def cleanup():
    """Stop all started tasks on system exit.

    Note: This only handles signals caught by the atexit module by default.
    SIGKILL, for instance, will not be caught, so cleanup is not guaranteed in
    all cases.
    """
    to_stop = STARTED_TASKS.copy()
    if to_stop:
        print "Cleaning up..."
    for task in to_stop:
        try:
            task.stop()
        except: # pylint: disable=W0702
            etype, value, trace = sys.exc_info()
            # Disregard no such process exceptions, print out the rest
            if not (isinstance(value, OSError) and value.errno == 3):
                print ''.join(format_exception(etype, value, trace, None))
            continue

def sigterm_handler(_sig, _frame):
    sys.exit(0)

# Register a SIGTERM handler if one is not already registered.
# By catching the signal atexit can do its thing in the case of SIGTERM.
if not signal.getsignal(signal.SIGTERM):
    signal.signal(signal.SIGTERM, sigterm_handler)

# TODO: create a wait_stopped() so that Tasks can be stopped in parallel

class Task(object):
    """Abstract class, the main unit of execution in PyREM.

    If you would like to define your own type of ``Task``, you should at least
    implement the ``_start``, ``_wait``, ``_stop``, and ``_reset`` methods.

    Every task that gets started will be stopped on Python exit, as long as that
    exit can be caught by the ``atexit`` module (e.g. pressing `Ctrl+C` will be
    caught, but sending `SIGKILL` will not be caught).

    Attributes:
        return_values (dict): Subclasses of ``Task`` should store all of their
            results in this field and document what the possible return values
            are.
    """

    def __init__(self):
        self._lock = RLock()
        self._status = TaskStatus.IDLE
        self.return_values = {}

    @synchronized
    def start(self, wait=False):
        """Start a task.

        This function depends on the underlying implementation of _start, which
        any subclass of ``Task`` should implement.

        Args:
            wait (bool): Whether or not to wait on the task to finish before
                returning from this function. Default `False`.

        Raises:
            RuntimeError: If the task has already been started without a
                subsequent call to ``reset()``.
        """
        if self._status is not TaskStatus.IDLE:
            raise RuntimeError("Cannot start %s in state %s" %
                               (self, self._status))
        self._status = TaskStatus.STARTED
        STARTED_TASKS.add(self)
        self._start()

        if wait:
            self.wait()

        return self.return_values

    def _start(self):
        raise NotImplementedError

    @synchronized
    def wait(self):
        """Wait on a task to finish and stop it when it has finished.

        Raises:
            RuntimeError: If the task hasn't been started or has already been
                stopped.

        Returns:
            The ``return_values`` of the task.
        """
        if self._status is not TaskStatus.STARTED:
            raise RuntimeError("Cannot wait on %s in state %s" %
                               (self, self._status))
        self._wait()
        self.stop()
        return self.return_values

    def _wait(self):
        pass

    @synchronized
    def stop(self):
        """Stop a task immediately.

        Raises:
            RuntimeError: If the task hasn't been started or has already been
                stopped.
        """
        if self._status is TaskStatus.STOPPED:
            return

        if self._status is not TaskStatus.STARTED:
            raise RuntimeError("Cannot stop %s in state %s" %
                               (self, self._status))
        self._stop()

        STARTED_TASKS.remove(self)
        self._status = TaskStatus.STOPPED

    def _stop(self):
        pass

    @synchronized
    def reset(self):
        """Reset a task.

        Allows a task to be started again, clears the ``return_values``.

        Raises:
            RuntimeError: If the task has not been stopped.
        """
        if self._status is not TaskStatus.STOPPED:
            raise RuntimeError("Cannot reset %s in state %s" %
                               (self, self._status))
        self._reset()
        self.return_values = {}
        self._status = TaskStatus.IDLE

    def _reset(self):
        pass

    def __repr__(self):
        # TODO: don't make the reprs so verbose, add a user defined name option?
        return "Task(status=%s, return_values=%s)" % (
            self._status, self.return_values)


# TODO: option for sending output to file
class SubprocessTask(Task):
    """A task to run a command as a subprocess on the local host.

    This process will be killed when this task is stopped.
    The return code of the process will be stored in
    ``return_values[\'retcode\']``.

    Args:
        command (list of str): The command to execute. Each command-line
            argument and flag should be a separate element in the command
            list unless ``shell = True``.

        quiet (bool): If `True`, the output of this command is not printed.
            Default `False`.

        return_output (bool): If `True`, the output of this command will be
            saved in ``return_values[\'stdout\']`` and
            ``return_values[\'stderr\']`` when the subprocess is allowed to
            finish (i.e. when it is waited on instead of being stopped).
            Default `False`.

            **quiet** and **return_output** shouldn't both be true.

        shell (bool): If `True`, allocate a shell to execute the process.
            See: ``subprocess.Popen``. Default `False`.

        require_success (bool): If `True` and if this task is waited on instead
            of being stopped, raises a ``RuntimeError`` if the subprocess has
            a return code other than `0`. Default `False`.
    """
    _DEVNULL = file(os.devnull, 'w')

    # pylint: disable=too-many-arguments
    def __init__(self, command, quiet=False, return_output=False, shell=False,
                 require_success=False):
        super(SubprocessTask, self).__init__()
        assert isinstance(command, list)
        self._command = [str(c) for c in command]
        self._require_success = require_success

        self._popen_kwargs = {}
        self._popen_kwargs['stdin'] = self._DEVNULL
        if shell:
            self._popen_kwargs['shell'] = True
            self._command = ' '.join(self._command)
        if return_output:
            self._popen_kwargs['stdout'] = PIPE
            self._popen_kwargs['stderr'] = PIPE
        elif quiet:
            self._popen_kwargs['stdout'] = self._DEVNULL
            self._popen_kwargs['stderr'] = self._DEVNULL

        self._process = None

    def _start(self):
        self._process = Popen(self._command, **self._popen_kwargs)

    def _wait(self):
        # Wait for process to finish
        output = self._process.communicate()
        # Raise error if necessary
        retcode = self._process.returncode
        if self._require_success and retcode:
            raise RuntimeError("Return code should have been 0, was %s" %
                               retcode)
        # Put return code and output in return_values
        self.return_values['stdout'] = output[0]
        self.return_values['stderr'] = output[1]
        self.return_values['retcode'] = retcode

    def _stop(self):
        if self._process.returncode is None:
            self._process.terminate()
            self._process.kill()

    def __repr__(self):
        return ("SubprocessTask(status=%s, return_values=%s, command=%s, "
                "popen_kwargs=%s)" % (
                    self._status, self.return_values, self._command,
                    self._popen_kwargs))


# TODO: option for sending remote output to remote file
class RemoteTask(SubprocessTask):
    """A task to run a command on a remote host over ssh.

    Any processes started on the remote host will be killed when this task is
    stopped (unless `kill_remote=False` is specified).

    ``return_values[\'retcode\']`` will contain the return code of the ssh
    command, which should currently be ignored.

    Attributes:
        host (str): The name of the host the task will run on.

    Args:
        host (str): The host to run on.

        command (list of str): The command to execute.

        quiet (bool): See ``SubprocessTask``.

        return_output (bool): See ``SubprocessTask``.

        kill_remote (bool): If `True`, all processes started on the remote
            server will be killed when this task is stopped.

        identity_file (str): Path to identity file passed to ssh. Default
            `None`.
    """
    def __init__(self, host, command, quiet=False, return_output=False,
                 kill_remote=True, identity_file=None):
        assert isinstance(command, list)
        self.host = host # TODO: disallow changing this attribute

        # Expand the path to the identity file
        if identity_file:
            identity_file = os.path.expanduser(identity_file)
        self._identity_file = identity_file

        # Log the other args
        self._remote_command = list(command)
        self._quiet = quiet
        self._return_output = return_output
        self._kill_remote = kill_remote

        # If kill remote, add the PID logging script to the command
        self._kill_remote = kill_remote
        if kill_remote:
            # Temp file holds the PIDs of processes started on remote host
            self._tmp_file_name = '/tmp/pyrem_procs-' + ''.join(
                random.SystemRandom().choice(
                    string.ascii_lowercase + string.digits)
                for _ in range(8))
            # TODO: Ending the user's command with ' & jobs ...' might not be
            #       safe. If the command ends in a &, for instance, this will
            #       just fail on the spot. Try to figure out a good way around
            #       this, but at least warn the user in RemoteTask's docstring\

            # TODO: handle shells like zsh where the -p flag doesn't just print
            #       out the PIDs
            command.append(' & jobs -p >%s ; wait' % self._tmp_file_name)

        if identity_file:
            ssh_cmd = ['ssh', '-i', identity_file, host, ' '.join(command)]
        else:
            ssh_cmd = ['ssh', host, ' '.join(command)]

        super(RemoteTask, self).__init__(ssh_cmd,
                                         quiet=quiet,
                                         return_output=return_output,
                                         shell=False)

    # TODO: capture the return code of the remote command

    def _stop(self):
        # First, stop the ssh command
        super(RemoteTask, self)._stop()

        # Silence the kill_proc to prevent messages about already killed procs
        if self._kill_remote:
            kill_proc = Popen(
                ['ssh', self.host, 'kill -9 `cat %s` ; rm %s' %
                 (self._tmp_file_name, self._tmp_file_name)],
                stdout=self._DEVNULL, stderr=self._DEVNULL, stdin=self._DEVNULL)
            kill_proc.wait()


    def __repr__(self):
        return ("RemoteTask(status=%s, return_values=%s, command=%s, "
                "popen_kwargs=%s)" % (
                    self._status, self.return_values, self._command,
                    self._popen_kwargs))


class Parallel(Task):
    """A task that executes several given tasks in parallel.

    Currently does not capture the return_values of the underlying tasks, this
    will be fixed in the future.

    Args:
        tasks (list of ``Task``): Tasks to execute.

        aggregate (bool): If `True`, will combine multiple RemoteTasks on the
            same host to use a single ssh session. Default `False`.

            Example: If you pass Parallel 6 tasks, 3 of which are running on
            host A and 3 of which are running on host B, aggregate will combine
            them into 2 tasks: one for host A and one for host B.

            Warning: The combined task will get its other options (``quiet``,
            ``kill_remote``, etc.) from one of the constituent commands. If you
            want to ensure the remote processes are killed, ensure that
            ``kill_remote`` is `True` for all processes on that host. If you
            rely on returned output for some of the commands, don't use
            aggregate (output will get mixed between all commands).
    """
    def __init__(self, tasks, aggregate=False):
        super(Parallel, self).__init__()
        self._tasks = tasks

        if aggregate:
            self._aggregate()

    def _aggregate(self):
        """Helper method to aggregate RemoteTasks into single ssh session."""
        # pylint: disable=W0212
        nonremote = [t for t in self._tasks if not isinstance(t, RemoteTask)]
        remote = [t for t in self._tasks if isinstance(t, RemoteTask)]

        host_dict = defaultdict(list)
        for task in remote:
            host_dict[task.host].append(task)

        aggregated = []
        for task_group in host_dict.values():
            # Build up combined command
            combined_cmd = []
            for task in task_group:
                if combined_cmd:
                    combined_cmd.append('&')
                combined_cmd.append(' '.join(task._remote_command))

            # Now, generated aggregate task
            t0 = task_group[0] # pylint: disable=C0103
            task = RemoteTask(
                t0.host, combined_cmd, t0._quiet, t0._return_output,
                t0._kill_remote, t0._identity_file)

            aggregated.append(task)

        self._tasks = nonremote + aggregated

    def _start(self):
        for task in self._tasks:
            task.start(wait=False)

    def _wait(self):
        # TODO: capture the return_values of the tasks
        for task in self._tasks:
            task.wait()

    def _stop(self):
        # TODO: this isn't quite right if there was an exception during _start
        # there needs to be some way to kill only the tasks that were started
        for task in self._tasks:
            task.stop()

    def _reset(self):
        for task in self._tasks:
            task.reset()

    def __repr__(self):
        return "ParallelTask(status=%s, return_values=%s, tasks=%s)" % (
                self._status, self.return_values, self._tasks
            )


class Sequential(Task):
    """A tasks that executes several given tasks in sequence.

    Currently does not capture the return_values of the underlying tasks, this
    will be fixed in the future.

    Args:
        tasks (list of ``Task``): Tasks to execute.
    """

    def __init__(self, tasks):
        super(Sequential, self).__init__()
        assert isinstance(tasks, list)
        self._tasks = tasks
        self._exception = None

        def run_thread(tasks):
            try:
                for task in tasks:
                    task.start(wait=True)
            except: # pylint: disable=W0702
                # Just record the exception and return, the main thread will
                # raise it
                self._exception = sys.exc_info()
                return

        self._thread = Thread(target=run_thread, args=(tasks,))

    def _start(self):
        self._thread.start()
        assert self._thread.is_alive()

    def _wait(self):
        # TODO: capture the return_values of the tasks
        self._thread.join()
        if self._exception:
            raise self._exception[0], self._exception[1], self._exception[2]

    def _stop(self):
        # FIXME this isn't threadsafe at all, have to have a way to signal
        #       the executing thread to stop
        for task in self._tasks:
            # pylint: disable=W0212
            if task._status in [TaskStatus.STARTED, TaskStatus.STOPPED]:
                task.stop()
            else:
                return

    def _reset(self):
        for task in self._tasks:
            task.reset()

    def __repr__(self):
        return "SequentialTask(status=%s, return_values=%s, tasks=%s)" % (
                self._status, self.return_values, self._tasks
            )
