Example PyREM Scripts
=====================

.. TODO: Add explanations of what each script does and what the benefits of PyREM are

Example 1
---------

Bash version
~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   #
   # A simple shell script to run iperf between two machines.


   HOST1='alpha'
   HOST2='bravo'

   ssh $HOST1 "iperf -s &"

   sleep 1

   ssh $HOST2 "iperf -c $HOST1"

   ssh $HOST1 "pkill -u $USER iperf"


PyREM version
~~~~~~~~~~~~~

.. code-block:: python

   '''
   A simple PyREM script to run iperf between two machines.
   '''

   import time
   from pyrem.host import RemoteHost

   # Declare two hosts.
   HOST1 = RemoteHost('alpha')
   HOST2 = RemoteHost('bravo')

   # Create tasks to be run on the hosts.
   server = HOST1.run(['iperf -s'], quiet=True)
   client = HOST2.run(['iperf -c alpha'])

   # Start the server task.
   server.start()

   # Wait for servers to be ready.
   time.sleep(1)

   # Run the client task.
   client.start(wait=True)

   # Clean up.
   server.stop()


Example 2
---------

Bash version
~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   #
   # A shell script to run iperf between multiple machines.

   SERVER_HOSTS=('alpha' 'bravo' 'charlie')

   # Start the servers.
   for host in ${SERVER_HOSTS[@]}
   do
     ssh ${host}.cs.washington.edu "iperf -s > /dev/null 2>&1 &"
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


PyREM version
~~~~~~~~~~~~~

.. code-block:: python

   '''
   A PyREM script to run iperf between multiple machines.
   '''

   import time
   from pyrem.host import RemoteHost, LocalHost
   from pyrem.task import Parallel, Sequential

   # Declare the hosts.
   SERVER_HOSTS = [RemoteHost(name + '.cs.washington.edu') for name in
                   ['alpha', 'bravo', 'charlie']]
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


Example 3
---------

Bash version
~~~~~~~~~~~~

.. code-block:: bash

    #!/bin/bash
    #
    # A shell script to get ping times between multiple machines.

    hosts=('alpha' 'bravo' 'charlie' 'delta')
    n_hosts=${#hosts[@]}

    declare -A pings

    for ((i=0; i<$n_hosts; i++))
    do
      for ((j=0; j<$n_hosts; j++))
      do
        cmd="ssh ${hosts[$i]} ping -q -c 3 ${hosts[$j]} | grep rtt | awk -F/ '{print \$5}'"
        pings[$i,$j]=$($cmd)
      done
    done

    # Add your favorite method for waiting on remote processes here.

    for ((i=0; i<$n_hosts; i++))
    do
      echo -n -e "\t${hosts[$i]}"
    done
    echo ""

    for ((i=0; i<$n_hosts; i++))
    do
      echo -n -e "${hosts[$i]}"
      for ((j=0; j<$n_hosts; j++))
      do
        echo -n -e "\t${pings[$i,$j]}"
      done
      echo ""
    done


PyREM version
~~~~~~~~~~~~~

.. code-block:: python


   '''
   A PyREM script to get ping times between multiple machines.
   '''

   import re
   import time

   from pyrem.host import RemoteHost
   from graphviz import Digraph

   # Declare the hosts.
   HOSTNAMES = ['alpha', 'bravo', 'charlie', 'delta']
   HOSTS = [RemoteHost(name) for name in HOSTNAMES]

   # Create tasks to be run on the hosts.
   tests = [src.run(['ping -c 10', dst.hostname], return_output=True)
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

   raw_input("\nPress [ENTER] to continue...\n")

   f = Digraph()
   for src in HOSTNAMES:
     for dst in HOSTNAMES:
       if src == dst:
         continue
       f.edge(src, dst, label=pings[src][dst])
   f.view()
