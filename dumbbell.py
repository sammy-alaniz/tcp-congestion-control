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


class DumbbellTopo(Topo):
    def build(self, delay=2):
        # The bandwidth (bw) is in Mbps, delay in milliseconds and queue size is in packets
        br_params = dict(bw=984, delay='{0}ms'.format(delay), max_queue_size=82*delay,
                         use_htb=True)  # backbone router interface tc params
        ar_params = dict(bw=252, delay='0ms', max_queue_size=(21*delay*20)/100,
                         use_htb=True)  # access router intf tc params
        # TODO: remove queue size from hosts and try.
        hi_params = dict(bw=960, delay='0ms', max_queue_size=80*delay, use_htb=True)  # host interface tc params

        # Create routers s1 to s4
        s1 = self.addSwitch('s1') # Backbone router #1
        s2 = self.addSwitch('s2') # Backbone router #2
        s3 = self.addSwitch('s3') # Access router #1
        s4 = self.addSwitch('s4') # Access router #2

        # Link backbone routers (s1 & s2) together
        self.addLink(s1, s2, cls=TCLink, **br_params) # Backbone Router #1 <-> Backbone Router #2

        # Link access routers (s3 & s4) to the backbone routers
        self.addLink(s1, s3, cls=TCLink, **ar_params) # Backbone Router #1 <-> Access Router #1
        self.addLink(s2, s4, cls=TCLink, **ar_params) # Backbone Router #2 <-> Access Router #2

        # Create the hosts h1 to h4, and link them to access router 1
        h1 = self.addHost('h1') # Source #1
        h2 = self.addHost('h2') # Source #2
        h3 = self.addHost('h3') # Receiver #1
        h4 = self.addHost('h4') # Receiver #2

        # Link the source hosts (h1 & h3) to access router 1 (s3)
        self.addLink(s3, h1, cls=TCLink, **hi_params) # Source #1 <-> Access router #1
        self.addLink(s3, h3, cls=TCLink, **hi_params) # Source #2 <-> Access router #1

        # Link the receiver hosts (h2 & h4) to access router 2 (s4)
        self.addLink(s4, h2, cls=TCLink, **hi_params) # Receiver #1 <-> Access Router #2
        self.addLink(s4, h4, cls=TCLink, **hi_params) # Receiver #2 <-> Access Router #2


def iperf3_command_builder(ip_address, port, interval, mtu, length_time_seconds, file_path, file_output_name) -> str:
    ''' Example: iperf3 --forceflush -c {0} -p 1111 -i 0.5 -M 1460 -N -t 20 > iperf_test_h1-h3_15s.txt
        All arguments must be passed in as strings'''
    command = ''
    command += 'iperf3' # iperf3 command
    command += ' '
    command += '--forceflush' # ensures that all data iperf collects is pushed to the txt file
    command += ' '
    command += '-c ' + ip_address # sets server ip address
    command += ' '
    command += '-p ' + port # sets server port
    command += ' '
    command += '-i ' + interval # sets interval to output data to txt file
    command += ' '
    command += '-M ' + mtu # sets the minimum transmission unit
    command += ' '
    command += '-N' # no delay
    command += ' '
    command += '-t ' + length_time_seconds # how long to send data for, in seconds
    command += ' > '
    command += file_path + file_output_name + '.txt' # file path and file name of data collected
    return command


def dumbbell_test():
    duration_one_ms = 0
    duration_two_ms = 0
    gap_time = 0
    """ Create and test a dumbbell network.
    """
    topo = DumbbellTopo(delay=21)
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

    sub_processes = dict()
    sub_processes[h3] = h3.popen('iperf -s -p 1111') # Start server on Receiver #1
    sub_processes[h4] = h4.popen('iperf -s -p 2222') # Start server on Receiver #2

    # Start client on Source #1
    command_one = iperf3_command_builder(h3_ip, '1111', '0.5', '1460', str(duration_one_ms),'/school/','output')
    print(command_one)
    sub_processes[h1] = h1.popen('iperf --forceflush -c {0} -p 1111 -i 0.5 -M 1460 -N -t 20 > iperf_test_h1-h3_15s.txt'.format(h3_ip), shell=True)
    print('Source #1 Client Started')
    # Start client on Source #2
    time.sleep(5)
    print('Source #2 Client Started')
    sub_processes[h2] = h2.popen('iperf --forceflush -c {0} -p 2222 -i 0.5 -M 1460 -N -t 15 > iperf_test_h2-h4_15s.txt'.format(h4_ip), shell=True)

    sub_processes[h1].wait() # Wait for Source #1 to stop sending
    sub_processes[h2].wait() # Wait for Source #2 to stop sending

    sub_processes[h3].terminate() # Stop Receiver #1 server
    sub_processes[h4].terminate() # Stop Receiver #2 server
    sub_processes[h3].wait() # Wait for Receiver #1 server to stop
    sub_processes[h4].wait() # Wait for Receiver #2 server to stop


    #topo.congestion_control_test(net)

    net.stop()

if __name__ == '__main__':
    clean_result = subprocess.run(['sudo','mn','-c'], stdout=subprocess.PIPE)
    dumbbell_test()



