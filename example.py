import re
import time

from pyrem.host import Host, LocalHost
from pyrem.task import Parallel, Sequential

REMOTE_HOSTS = [Host(name) for name in ['spyhunter', 'breakout', 'zork']]
LOCAL_HOST = LocalHost()

SERVERS = Parallel([host.run(['iperf', '-s'], quiet=True)
                    for host in REMOTE_HOSTS])
CLIENTS = Sequential([LOCAL_HOST.run(['iperf', '-c', host.hostname])
                      for host in REMOTE_HOSTS])

SERVERS.start()
time.sleep(2)
CLIENTS.start(wait=True)
SERVERS.stop()
