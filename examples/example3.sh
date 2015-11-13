#!/bin/bash
#
# A shell script to get ping times between multiple machines.

hosts=('candy' 'carrey' 'qbert' 'zork')
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
