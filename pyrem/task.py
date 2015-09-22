"""Contains the main unit of execution in PyREM, the task.

Tasks should be composable and should be able to be executed synchronously or
asynchronously. There should be some easy way of combining tasks both
sequentially and in parallel.
"""

import atexit
import os
import random
import string

from enum import Enum
from subprocess import Popen, PIPE
from threading import Thread


TaskStatus = Enum('TaskStatus', 'IDLE STARTED STOPPED')

STARTED_TASKS = set() # TODO: figure out why some IDLE tasks end up here

def cleanup():
    to_stop = STARTED_TASKS.copy()
    if to_stop:
        print "Cleaning up..."
    for task in to_stop:
        task.stop()

atexit.register(cleanup)


# TODO: create a wait_stopped() so that Tasks can be stopped in parallel


class Task(object):
    def __init__(self):
        self._status = TaskStatus.IDLE
        self.return_value = None

    def start(self, wait=False):
        if self._status is not TaskStatus.IDLE:
            raise RuntimeError("Cannot start task in state %s" % self._status)
        STARTED_TASKS.add(self)
        self._start()
        self._status = TaskStatus.STARTED

        if wait:
            self.wait()

        return self.return_value

    def _start(self):
        raise NotImplementedError

    def wait(self):
        if self._status is not TaskStatus.STARTED:
            raise RuntimeError("Cannot wait on task in state %s" % self._status)
        self._wait()
        self.stop()
        return self.return_value

    def _wait(self):
        pass

    def stop(self):
        if self._status is TaskStatus.STOPPED:
            return

        if self._status is not TaskStatus.STARTED:
            raise RuntimeError("Cannot stop task in state %s" % self._status)
        self._stop()
        self._status = TaskStatus.STOPPED

        STARTED_TASKS.remove(self)

    def _stop(self):
        pass

    def reset(self):
        if self._status is not TaskStatus.STOPPED:
            raise RuntimeError("Cannot reset task in state %s" % self._status)
        self._reset()
        self.return_value = None
        self._status = TaskStatus.IDLE

    def _reset(self):
        pass

    def __repr__(self):
        return "Task(status=%s, return_value=%s)" % (
            self._status, self.return_value)

# TODO: define a remote task that kills the remote processes started by it in
#       stop


class SubprocessTask(Task):
    DEVNULL = file(os.devnull, 'w')

    def __init__(self, command, quiet=False, return_output=False, shell=False):
        super(SubprocessTask, self).__init__()
        self._command = command

        self._popen_kwargs = {}
        self._popen_kwargs['stdin'] = self.DEVNULL
        if shell:
            self._popen_kwargs['shell'] = True
            self._command = ' '.join(self._command)
        if return_output:
            self._popen_kwargs['stdout'] = PIPE
            self._popen_kwargs['stderr'] = PIPE
        elif quiet:
            self._popen_kwargs['stdout'] = self.DEVNULL
            self._popen_kwargs['stderr'] = self.DEVNULL

        self._process = None

    def _start(self):
        self._process = Popen(self._command, **self._popen_kwargs)

    def _wait(self):
        output = self._process.communicate()
        # TODO: add an option to require return code 0 or raise exception
        retcode = self._process.returncode
        self.return_value = {
            'stdout': output[0],
            'stderr': output[1],
            'retcode': retcode
        }

    def _stop(self):
        if self._process.returncode is None:
            self._process.terminate()
            self._process.kill()

    def __repr__(self):
        return ("SubprocessTask(status=%s, return_value=%s, command=%s, "
                "popen_kwargs=%s)" % (
                    self._status, self.return_value, self._command,
                    self._popen_kwargs))

# TODO: add an option to skip the tmpfile, pgrep, and cleanup stuff
class RemoteTask(SubprocessTask):
    def __init__(self, host, command, quiet=False, return_output=False):
        assert isinstance(command, list)
        self._host = host
        # Temp file holds the PIDs of processes started on remote host
        self._tmp_file_name = '/tmp/pyrem_procs-' + ''.join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(8))
        ssh_command = ['ssh', host, ' '.join(command) +
                       ' & pgrep -P $$ >%s' % self._tmp_file_name]

        super(RemoteTask, self).__init__(ssh_command, quiet=quiet,
                                         return_output=return_output,
                                         shell=False)

    def _stop(self):
        super(RemoteTask, self)._stop()
        # Silence the kill_proc to prevent messages about already killed procs
        kill_proc = Popen(
            ['ssh', self._host, 'kill -9 `cat %s`' % self._tmp_file_name],
            stdout=self.DEVNULL, stderr=self.DEVNULL, stdin=self.DEVNULL)
        kill_proc.wait()


    def __repr__(self):
        return ("RemoteTask(status=%s, return_value=%s, command=%s, "
                "popen_kwargs=%s)" % (
                    self._status, self.return_value, self._command,
                    self._popen_kwargs))


class Parallel(Task):
    def __init__(self, tasks):
        super(Parallel, self).__init__()
        self._tasks = tasks

    def _start(self):
        for task in self._tasks:
            task.start(wait=False)

    def _wait(self):
        for task in self._tasks:
            task.wait()

    def _stop(self):
        for task in self._tasks:
            task.stop()

    def _reset(self):
        for task in self._tasks:
            task.reset()

    def __repr__(self):
        return "ParallelTask(status=%s, return_value=%s, tasks=%s)" % (
                self._status, self.return_value, self._tasks
            )


class Sequential(Task):
    def __init__(self, tasks):
        super(Sequential, self).__init__()
        assert isinstance(tasks, list)
        self._tasks = tasks

        def run_thread(tasks):
            for task in tasks:
                task.start(wait=True)

        self._thread = Thread(target=run_thread, args=(tasks,))

    def _start(self):
        self._thread.start()
        assert self._thread.is_alive()

    def _wait(self):
        self._thread.join()

    def _stop(self):
        for task in self._tasks:
            # FIXME this isn't threadsafe at all, have to have a way to signal
            #       the executing thread
            task.stop()

    def _reset(self):
        for task in self._tasks:
            task.reset()

    def __repr__(self):
        return "SequentialTask(status=%s, return_value=%s, tasks=%s)" % (
                self._status, self.return_value, self._tasks
            )
