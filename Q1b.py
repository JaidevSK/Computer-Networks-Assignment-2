from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
import time
import os


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
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)



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


setLogLevel( 'info' ) # I set the log level to info
net.start() # Then the network is started
info("***Starting iperf3 server on h7\n") # I log that I am starting the iperf3 server on h7
h7 = net.get('h7')  # I get the host h7
h7.cmd('iperf3 -s &')  # I start the iperf3 server on h7

info("***Starting TCPdump on h7 and h1, h3, h4\n")
h7_tcpdump = h7.popen(f"tcpdump -i {h7.defaultIntf()} -w /tmp/h7_capture_b_{congestion_control}.pcap")
h1 = net.get('h1')
h1_tcpdump = h1.popen(f"tcpdump -i {h1.defaultIntf()} -w /tmp/h1_capture_b_{congestion_control}.pcap")
h3 = net.get('h3')
h3_tcpdump = h3.popen(f"tcpdump -i {h3.defaultIntf()} -w /tmp/h3_capture_b_{congestion_control}.pcap")
h4 = net.get('h4')
h4_tcpdump = h4.popen(f"tcpdump -i {h4.defaultIntf()} -w /tmp/h4_capture_b_{congestion_control}.pcap")

# h1 iperf3 (starts at T=0s, runs for 150s) / 2
info("***Starting iperf3 client on h1\n")
h1_command = f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 150 -C {congestion_control}'
h1_process = h1.popen(h1_command, shell=True)
h1_start_time = time.time()

# h3 iperf3 (starts at T=15s, runs for 120s) / 2 
h3_start_delay = 7.5
h3_command = f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 120 -t 120 -C {congestion_control}'
h3_process = None
h3_start_time = None
h3_started = False 

# h4 iperf3 (starts at T=30s, runs for 90s) / 2
h4_start_delay = 15
h4_command = f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 90 -C {congestion_control}'
h4_process = None
h4_start_time = None
h4_started = False 

script_start_time = time.time()

while True:
    current_time = time.time() - script_start_time

    # Start h3 if delay is reached
    if not h3_started and current_time >= h3_start_delay:
        info("***Starting iperf3 client on h3\n")
        h3_process = h3.popen(h3_command, shell=True)
        h3_start_time = time.time()
        h3_started = True

    # Start h4 if delay is reached
    if not h4_started and current_time >= h4_start_delay: 
        info("***Starting iperf3 client on h4\n")
        h4_process = h4.popen(h4_command, shell=True)
        h4_start_time = time.time()
        h4_started = True

    # Check for h1 timeout or completion
    if h1_process is not None:
        if h1_process.poll() is not None or time.time() - h1_start_time > 75:
            if h1_process.poll() is None:
                info("***h1 iperf3 timeout reached, terminating\n")
                h1_process.terminate()
            h1_process = None  

    # Check for h3 timeout or completion
    if h3_process is not None:
        if h3_process.poll() is not None or time.time() - h3_start_time > 60:
            if h3_process.poll() is None:
                info("***h3 iperf3 timeout reached, terminating\n")
                h3_process.terminate()
            h3_process = None  

    # Check for h4 timeout or completion
    if h4_process is not None:
        if h4_process.poll() is not None or time.time() - h4_start_time > 45:
            if h4_process.poll() is None:
                info("***h4 iperf3 timeout reached, terminating\n")
                h4_process.terminate()
            h4_process = None 

    # Break if all processes are finished
    if h1_process is None and h3_process is None and h4_process is None:
        break

    time.sleep(1)

os.system('mkdir -p ./pcaps_captured_trail')
os.system('mv /tmp/*.pcap ./pcaps_captured_trail/')

info("***Stopping TCPdump\n")
h7_tcpdump.terminate()
h1_tcpdump.terminate()
h3_tcpdump.terminate()
h4_tcpdump.terminate()

info("***Stopping network\n")
net.stop()


# References:
# http://mininet.org/walkthrough/
# https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py
# https://github.com/mininet/mininet/blob/master/examples/popen.py

