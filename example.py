from pyrem.host import Host, LocalHost
from pyrem.task import SubprocessTask

spyhunter = Host('spyhunter.cs.washington.edu')
localhost = LocalHost()

server = localhost.run(['iperf',  '-s'])
client = spyhunter.run(['iperf',  '-c', localhost.hostname])

server.start()
client.run()
server.stop()
