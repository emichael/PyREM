from pyrem.task import Task, TaskStatus

class DummyTask(Task):
    def _start(self):
        pass

    def _wait(self):
        pass

    def _stop(self):
        pass


class TestDummyTask(object):
    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""
        pass

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""
        pass

    def setup(self):
        self.task = DummyTask()

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        pass

    def test_status(self):
        assert self.task._status == TaskStatus.IDLE
        self.task.start()
        assert self.task._status == TaskStatus.STARTED
        self.task.wait()
        assert self.task._status == TaskStatus.STOPPED

    def test_status2(self):
        self.task.start(wait=True)
        assert self.task._status == TaskStatus.STOPPED
