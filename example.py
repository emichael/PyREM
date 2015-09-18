import re

from pyrem.host import Host, LocalHost
from pyrem.task import SubprocessTask

spyhunter = Host('spyhunter.cs.washington.edu')
localhost = LocalHost()

server = localhost.run(['iperf',  '-s'], quiet=True)
client = spyhunter.run(['iperf',  '-c', localhost.hostname], return_output=True)

server.start()
client.run()
server.stop()

output = client.return_value['stdout']
s = re.search('Bandwidth.*]\s+[^\s]+\s+[^\s]+\s+([^\s]+\s+[^\s]+)', output, re.S)
print s.group(1)
