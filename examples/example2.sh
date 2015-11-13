#/bin/bash
'''
A shell script to run iperf between multiple machines.
'''

SERVER_HOSTS=('tradewars', 'spyhunter', 'zork')

# Start the servers.
for host in ${SERVER_HOSTS[@]}
do
  ssh ${host}.cs.washington.edu "iperf -s &"
done

sleep 1

# Run the clients one by one.
for host in ${SERVER_HOSTS[@]}
do
  iperf -c ${host}.cs.washington.edu
done

# Cleanup all the servers.
for host in ${SERVER_HOSTS[@]}
do
  ssh ${host}.cs.washington.edu "pkill -u $USER iperf"
done
