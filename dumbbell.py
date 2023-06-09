import argparse
#from time import sleep, mktime
import time
import subprocess
import csv
from datetime import datetime
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections, quietRun
from mininet.log import info, lg, setLogLevel
from mininet.cli import CLI

import os
import signal
import sys


class DumbbellTopo(Topo):
    def build(self, delay=2):
            # The bandwidth (bw) is in Mbps, delay in milliseconds and queue size is in packets
            # br_params = dict(bw=984, delay='{0}ms'.format(delay), max_queue_size=82*delay,
                            # use_htb=True)  # backbone router interface tc params
            # ar_params = dict(bw=252, delay='0ms', max_queue_size=(21*delay*20)/100,
                            # use_htb=True)  # access router intf tc params
            # TODO: remove queue size from hosts and try.
            # hi_params = dict(bw=960, delay='0ms', max_queue_size=80*delay, use_htb=True)  # host interface tc params
            br_params = dict(bw=984, delay='{0}ms'.format(delay), use_htb=True)
            hi_params = dict(bw=960, use_htb=True)

            # Create routers s1 to s4
            s1 = self.addSwitch('s1')
            s2 = self.addSwitch('s2')
            s3 = self.addSwitch('s3')
            s4 = self.addSwitch('s4')

            # Link backbone routers (s1 & s2) together
            self.addLink(s1, s2, cls=TCLink, **br_params)

            # Link access routers (s3 & s4) to the backbone routers
            # self.addLink(s1, s3, cls=TCLink, **ar_params)
            # self.addLink(s2, s4, cls=TCLink, **ar_params)
            self.addLink(s1, s3, cls=TCLink)
            self.addLink(s2, s4, cls=TCLink)

            # Create the hosts h1 to h4, and link them to access router 1
            h1 = self.addHost('h1')
            h2 = self.addHost('h2')
            h3 = self.addHost('h3')
            h4 = self.addHost('h4')

            # Link the source hosts (h1 & h3) to access router 1 (s3)
            self.addLink(s3, h1, cls=TCLink, **hi_params)
            self.addLink(s3, h3, cls=TCLink, **hi_params)

            # Link the receiver hosts (h2 & h4) to access router 2 (s4)
            self.addLink(s4, h2, cls=TCLink, **hi_params)
            self.addLink(s4, h4, cls=TCLink, **hi_params)

            # Configure the vertical links connecting the access routers to the backbone routers
            bufferSize = ((20 * 21 * 1500) / (100 * 1000)) * delay
            quietRun(f'tc qdisc add dev s1-eth2 root tbf rate 252mbit burst 100kb limit {bufferSize}kb')
            quietRun(f'tc qdisc add dev s3-eth1 root tbf rate 252mbit burst 100kb limit {bufferSize}kb')
            quietRun(f'tc qdisc add dev s2-eth2 root tbf rate 252mbit burst 100kb limit {bufferSize}kb')
            quietRun(f'tc qdisc add dev s4-eth1 root tbf rate 252mbit burst 100kb limit {bufferSize}kb')

def change_tcp_congestion_algorithm(algo):
    quietRun(f"sysctl -w net.ipv4.tcp_congestion_control={algo}")

def dumbbell_test(delay=21, algo='reno', duration_one=2000, duration_two=1750, sleep=250):
    sub_processes = dict()

    try:
            
        curr_delay = delay
        curr_algo = algo

        change_tcp_congestion_algorithm(curr_algo)
    
        duration_one_seconds = duration_one
        duration_two_seconds = duration_two
        sleep_time_seconds = sleep
    
        """ Create and test a dumbbell network.
        """
        topo = DumbbellTopo(curr_delay)
        net = Mininet(topo)
        net.start()
    
        h1 = net.get('h1')
        h2 = net.get('h2')
        h3 = net.get('h3')
        h4 = net.get('h4')
    
        h1_ip = h1.IP() # Source #1
        h2_ip = h2.IP() # Source #2
        h3_ip = h3.IP() # Receiver #1 
        h4_ip = h4.IP() # Receiver #2
    
        
        sub_processes[h3] = h3.popen('iperf -s -p 1111') # Start server on Receiver #1
        sub_processes[h4] = h4.popen('iperf -s -p 2222') # Start server on Receiver #2
    
        # Start client on Source #1
    
        sub_processes[h1] = h1.popen('iperf --forceflush -c {0} -p 1111 -i 1 -f m -N -t {1} > iperf_test_h1-h3_15s.txt'.format(h3_ip, duration_one_seconds), shell=True)
        cwd_ss_one = h1.popen('watch -n 1 \'ss --tcp -i dst {0} >> host-one-ss-out.txt\''.format(h3_ip), shell=True)
    
        time.sleep(sleep_time_seconds)
    
        # Start client on Source #2
        print('Source #2 Client Started')
        sub_processes[h2] = h2.popen('iperf --forceflush -c {0} -p 2222 -i 1 -f m -N -t {1} > iperf_test_h2-h4_15s.txt'.format(h4_ip, duration_two_seconds), shell=True)
        cwd_ss_two = h2.popen('watch -n 1 \'ss --tcp -i dst {0} >> host-two-ss-out.txt\''.format(h4_ip), shell=True)
    
        sub_processes[h1].wait() # Wait for Source #1 to stop sending
        sub_processes[h2].wait() # Wait for Source #2 to stop sending
    
        sub_processes[h3].terminate() # Stop Receiver #1 server
        sub_processes[h4].terminate() # Stop Receiver #2 server
        sub_processes[h3].wait() # Wait for Receiver #1 server to stop
        sub_processes[h4].wait() # Wait for Receiver #2 server to stop
    
        cwd_ss_one.terminate()
        cwd_ss_two.terminate()
        cwd_ss_one.wait()
        cwd_ss_two.wait()
    
        #topo.congestion_control_test(net)
    
        net.stop()
    except KeyboardInterrupt:
        quietRun('sudo pkill -9 iperf')
        sys.exit()


if __name__ == '__main__':
    clean_result = subprocess.run(['sudo','mn','-c'], stdout=subprocess.PIPE)
    dumbbell_test(21, 'reno')



