import re
import time
from pyrem.utils import log_output, stop_log_output
log_output("foo.txt")

from pyrem.host import Host, LocalHost
from pyrem.task import Parallel, Sequential

REMOTE_HOSTS = [Host(name + '.cs.washington.edu') for name in
                ['spyhunter', 'breakout', 'zork']]
LOCAL_HOST = LocalHost()

SERVERS = Parallel([host.run(['iperf', '-s'], quiet=True)
                    for host in REMOTE_HOSTS])
CLIENTS = Sequential([LOCAL_HOST.run(['iperf', '-t', 3, '-c', host.hostname])
                      for host in REMOTE_HOSTS])

SERVERS.start()
time.sleep(2)
test = "foo"
print test
CLIENTS.start(wait=True)
SERVERS.stop()
# stop_log_output()
print "Hello world"
