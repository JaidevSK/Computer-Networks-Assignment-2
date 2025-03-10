from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
import time
import os

val_loss = int(input("Enter the value of val_loss (1 or 5)%: "))
print("LOSS", val_loss, type(val_loss))

class A2Q1(Topo):
    def build(self):
        # I first create the hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # I will now add links as given in diagram
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(h6, s4)
        self.addLink(h7, s4)
        
        # I will now add the remaining links between switches
        self.addLink(s1, s2, bw=100)
        self.addLink(s2, s3, bw=50, loss=val_loss)
        self.addLink(s3, s4, bw=100)



topo = A2Q1() # I create the topology that is given in Question 1
net = Mininet(topo=topo)

print("Starting network")
print("Enter the congestion control algorithm you want to use: 1. cubic 2. vegas 3. scalable")
congestion_control = int(input("Enter the number 1, 2, 3: "))
if congestion_control == 1:
    congestion_control = 'cubic'
elif congestion_control == 2:
    congestion_control = 'vegas'
elif congestion_control == 3:
    congestion_control = 'scalable'
else:
    print("Invalid input. Exiting")
    exit(1)

condition = input("Input Condition 1 or 2a, 2b, 2c: ")
if condition == "1":
    setLogLevel('info')
    net.start()
    info("***Starting iperf3 server on h7\n")
    h7 = net.get('h7')
    h7.cmd('iperf3 -s &')
    info("***Starting TCPdump on h7 and h3\n")
    h7.popen(f"tcpdump -i {h7.defaultIntf()} -w /tmp/h7_capture_d1_{congestion_control}.pcap")
    h3 = net.get('h3')
    h3.popen(f"tcpdump -i {h3.defaultIntf()} -w /tmp/h3_capture_d1_{congestion_control}.pcap")
    info("***Starting iperf3 client on h3\n")
    h3.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    time.sleep(30)
    if val_loss == 5:
        os.system('mkdir -p ./pcaps_captured_loss5')
        os.system('mv /tmp/*.pcap ./pcaps_captured_loss5/')
    else:
        os.system('mkdir -p ./pcaps_captured')
        os.system('mv /tmp/*.pcap ./pcaps_captured/')
    info("***Stopping network\n")
    net.stop()

elif condition == "2a":
    setLogLevel('info')
    net.start()
    info("***Starting iperf3 server on h7\n")
    h7 = net.get('h7')
    h7.cmd('iperf3 -s &')
    info("***Starting TCPdump on h7, h1, and h2\n")
    h7.popen(f"tcpdump -i {h7.defaultIntf()} -w /tmp/h7_capture_d2a_{congestion_control}.pcap")
    h1 = net.get('h1')
    h1.popen(f"tcpdump -i {h1.defaultIntf()} -w /tmp/h1_capture_d2a_{congestion_control}.pcap")
    h2 = net.get('h2')
    h2.popen(f"tcpdump -i {h2.defaultIntf()} -w /tmp/h2_capture_d2a_{congestion_control}.pcap")
    info("***Starting iperf3 client on h1\n")
    h1.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    info("***Starting iperf3 client on h2\n")
    h2.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    time.sleep(30)
    if val_loss == 5:
        os.system('mkdir -p ./pcaps_captured_loss5')
        os.system('mv /tmp/*.pcap ./pcaps_captured_loss5/')
    else:
        os.system('mkdir -p ./pcaps_captured')
        os.system('mv /tmp/*.pcap ./pcaps_captured/')
    info("***Stopping network\n")
    net.stop()

elif condition == "2b":
    setLogLevel('info')
    net.start()
    info("***Starting iperf3 server on h7\n")
    h7 = net.get('h7')
    h7.cmd('iperf3 -s &')
    info("***Starting TCPdump on h7, h1, and h3\n")
    h7.popen(f"tcpdump -i {h7.defaultIntf()} -w /tmp/h7_capture_d2b_{congestion_control}.pcap")
    h1 = net.get('h1')
    h1.popen(f"tcpdump -i {h1.defaultIntf()} -w /tmp/h1_capture_d2b_{congestion_control}.pcap")
    h3 = net.get('h3')
    h3.popen(f"tcpdump -i {h3.defaultIntf()} -w /tmp/h3_capture_d2b_{congestion_control}.pcap")
    info("***Starting iperf3 client on h1\n")
    h1.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    info("***Starting iperf3 client on h3\n")
    h3.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    time.sleep(30)
    if val_loss == 5:
        os.system('mkdir -p ./pcaps_captured_loss5')
        os.system('mv /tmp/*.pcap ./pcaps_captured_loss5/')
    else:
        os.system('mkdir -p ./pcaps_captured')
        os.system('mv /tmp/*.pcap ./pcaps_captured/')
    info("***Stopping network\n")
    net.stop()

elif condition == "2c":
    setLogLevel('info')
    net.start()
    info("***Starting iperf3 server on h7\n")
    h7 = net.get('h7')
    h7.cmd('iperf3 -s &')
    info("***Starting TCPdump on h7, h1, h3, and h4\n")
    h7.popen(f"tcpdump -i {h7.defaultIntf()} -w /tmp/h7_capture_d2c_{congestion_control}.pcap")
    h1 = net.get('h1')
    h1.popen(f"tcpdump -i {h1.defaultIntf()} -w /tmp/h1_capture_d2c_{congestion_control}.pcap")
    h3 = net.get('h3')
    h3.popen(f"tcpdump -i {h3.defaultIntf()} -w /tmp/h3_capture_d2c_{congestion_control}.pcap")
    h4 = net.get('h4')
    h4.popen(f"tcpdump -i {h4.defaultIntf()} -w /tmp/h4_capture_d2c_{congestion_control}.pcap")
    info("***Starting iperf3 client on h1\n")
    h1.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    info("***Starting iperf3 client on h3\n")
    h3.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    info("***Starting iperf3 client on h4\n")
    h4.cmd(f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 30 -C {congestion_control} &')
    time.sleep(30)
    if val_loss == 5:
        os.system('mkdir -p ./pcaps_captured_loss5')
        os.system('mv /tmp/*.pcap ./pcaps_captured_loss5/')
    else:
        os.system('mkdir -p ./pcaps_captured')
        os.system('mv /tmp/*.pcap ./pcaps_captured/')
    info("***Stopping network\n")
    net.stop()


else:
    print("Invalid input. Exiting")
    exit(1)

# References:
# http://mininet.org/walkthrough/
# https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py
# https://github.com/mininet/mininet/blob/master/examples/popen.py
# https://mininet.org/api/classmininet_1_1link_1_1TCIntf.html
