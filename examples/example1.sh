#!/bin/bash
#
# A simple shell script to run iperf between two machines.


HOST1='tradewars.cs.washington.edu'
HOST2='spyhunter.cs.washington.edu'

ssh $HOST1 "iperf -s &"

sleep 1

ssh $HOST2 "iperf -c $HOST1"

ssh $HOST1 "pkill -u $USER iperf"
