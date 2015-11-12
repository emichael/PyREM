'''
A simple PyREM script to run iperf between two machines.
'''

import time
from pyrem.host import RemoteHost

# Declare two hosts.
HOST1 = RemoteHost('tradewars.cs.washington.edu')
HOST2 = RemoteHost('spyhunter.cs.washington.edu')

# Create tasks to be run on the hosts.
server = HOST1.run(['iperf -s'], quiet=True)
client = HOST2.run(['iperf -c tradewars.cs.washington.edu'])

# Start the server task.
server.start()

# Wait for servers to be ready.
time.sleep(1)

# Run the client task.
client.start(wait=True)

# Clean up.
server.stop()
