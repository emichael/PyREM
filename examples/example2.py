'''
A PyREM script to run iperf between multiple machines.
'''

import time
from pyrem.host import RemoteHost, LocalHost
from pyrem.task import Parallel, Sequential

# Declare the hosts.
SERVER_HOSTS = [RemoteHost(name + '.cs.washington.edu') for name in
                ['zork', 'spyhunter', 'tradewars']]
CLIENT_HOST = LocalHost()

# Create tasks to be run on the hosts.
servers = Parallel([host.run(['iperf -s'], quiet=True)
                    for host in SERVER_HOSTS])
client = Sequential([CLIENT_HOST.run(['iperf', '-c', host.hostname])
                    for host in SERVER_HOSTS])

# Start all the servers in parallel.
servers.start()

# Wait for servers to be ready.
time.sleep(1)

# Run the client task.
client.start(wait=True)

# Clean up.
servers.stop()
