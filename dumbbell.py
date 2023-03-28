import argparse
from time import sleep, mktime
import subprocess
import csv
from datetime import datetime
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections, quietRun
from mininet.log import info, lg, setLogLevel
from mininet.cli import CLI

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
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Link backbone routers (s1 & s2) together
        self.addLink(s1, s2, cls=TCLink, **br_params)

        # Link access routers (s3 & s4) to the backbone routers
        self.addLink(s1, s3, cls=TCLink, **ar_params)
        self.addLink(s2, s4, cls=TCLink, **ar_params)

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






def dumbbell_test():
    """ Create and test a dumbbell network.
    """
    topo = DumbbellTopo(delay=21)
    net = Mininet(topo)
    net.start()

    print("Dumping host connections...")
    dumpNodeConnections(net.hosts)

    print("Testing network connectivity...")
    h1, h2 = net.get('h1', 'h2')
    h3, h4 = net.get('h3', 'h4')

    CLI( net )
    net.stop()




if __name__ == '__main__':
    dumbbell_test()
