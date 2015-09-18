import re
import time

from pyrem.host import Host, LocalHost
from pyrem.task import Parallel

remote_hosts = [Host(name) for name in ['spyhunter', 'breakout', 'zork']]
localhost = LocalHost()

servers = Parallel([host.run(['iperf', '-s'], quiet=True)
                    for host in remote_hosts])
clients = [localhost.run(['iperf', '-c', host.hostname], return_output=True)
           for host in remote_hosts]

servers.start()
time.sleep(1)
for client in clients:
    client.run()
    output = client.return_value['stdout']
    s = re.search(
        r'Client connecting to (\w+).*'
        r'Bandwidth.*]\s+[^\s]+\s+[^\s]+\s+([^\s]+\s+[^\s]+)',
        output, re.S)
    print "%s: %s" % (s.group(1), s.group(2))
servers.stop()

kill_servers = Parallel(
    [host.run(['pkill', '-f', 'iperf'], quiet=True) for host in remote_hosts])
kill_servers.run()
