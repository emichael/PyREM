"""Contains the main unit of execution in PyREM, the task.

Tasks should be composable and should be able to be executed synchronously or
asynchronously. There should be some easy way of combining tasks both
sequentially and in parallel.
"""

import os

from enum import Enum
from subprocess import Popen, PIPE


TaskStatus = Enum('TaskStatus', 'IDLE STARTED STOPPED')

# TODO: create a global register of started tasks and add an exit hook that
#        ensures that Taks.stop() is called for each task before Python exits

# TODO: create a wait_stopped() so that Tasks can be stopped in parallel


class Task(object):
    def __init__(self):
        self._status = TaskStatus.IDLE
        self.return_value = None

    def start(self, wait=False):
        if self._status is not TaskStatus.IDLE:
            raise RuntimeError("Cannot start task in state %s" % self._status)
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

# TODO: define a remote task that kills the remote processes started by it in
#       stop

class SubprocessTask(Task):
    DEVNULL = file(os.devnull, 'w')

    def __init__(self, command, quiet=False, return_output=False):
        super(SubprocessTask, self).__init__()
        self._command = command

        self._popen_kwargs = {}
        if return_output:
            self._popen_kwargs['stdin'] = self.DEVNULL
            self._popen_kwargs['stdout'] = PIPE
            self._popen_kwargs['stderr'] = PIPE
        elif quiet:
            self._popen_kwargs['stdin'] = self.DEVNULL
            self._popen_kwargs['stdout'] = self.DEVNULL
            self._popen_kwargs['stderr'] = self.DEVNULL

        self._process = None

    def _start(self):
        self._process = Popen(self._command, **self._popen_kwargs)

    def _wait(self):
        output = self._process.communicate()
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
