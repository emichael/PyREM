'''
A PyREM script to get ping times between multiple machines.
'''

import re
import time
from pyrem.host import RemoteHost

# Declare the hosts.
HOSTNAMES = ['candy', 'carrey', 'qbert', 'zork']
HOSTS = [RemoteHost(name) for name in HOSTNAMES]

# Create tasks to be run on the hosts.
tests = [src.run(['ping -c 5', dst.hostname], return_output=True)
          for src in HOSTS
            for dst in HOSTS]

# Start all the tests in parallel.
for t in tests:
  t.start()

pings = {host:{} for host in HOSTNAMES}

# Process the ping times.
for t in tests:
  t.wait()
  output = t.return_values['stdout']
  src = t.host
  dst = re.search('PING (.+?)[. ]', output).group(1)
  rtt = re.search('rtt (.+?) = (.+?)/(.+?)/', output).group(3)

  pings[src][dst] = rtt

# Pretty print.
for host in HOSTNAMES:
  print '\t', host,

for src in HOSTNAMES:
  print '\n', src,
  for dst in HOSTNAMES:
    print '\t', pings[src][dst],
