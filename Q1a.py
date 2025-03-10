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

print("Starting network") # I log that I am starting the network
print("Enter the congestion control algorithm you want to use: 1. cubic 2. vegas 3. scalable")
congestion_control = int(input("Enter the number 1, 2, 3: ")) # The user is asked to enter the congestion control algorithm
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
info("***Starting TCPdump on h7 and h1\n") # I log that I am starting tcpdump on h7 and h1
h1 = net.get('h1') # I get the host h1
h7_tcpdump = h7.popen(f"tcpdump -i {h7.defaultIntf()} -w /tmp/h7_capture_a_{congestion_control}.pcap") 
h1_tcpdump = h1.popen(f"tcpdump -i {h1.defaultIntf()} -w /tmp/h1_capture_a_{congestion_control}.pcap")
info("***Starting iperf3 client on h1\n") # I log that I am starting the iperf3 client on h1 and start the iperf client on h1
iperf_command = f'iperf3 -c 10.0.0.7 -p 5201 -b 10M -P 10 -t 150 -C {congestion_control}'
process = h1.popen(iperf_command, shell=True) # I start the iperf3 client on h1

start_time = time.time() # I get the start time and as I mentioned in the report, this will run only for 75 seconds
while process.poll() is None: # I check if the process is still running
    if time.time() - start_time > 75: # If the time is more than 75 seconds, I terminate the process
        info("***iperf3 timeout reached, terminating\n") # If the time is more than 75 seconds, I log that the iperf3 timeout is reached
        process.terminate() # and I terminate the process
        break
    time.sleep(1)

info("***Stopping TCPdump\n") # I log that I am stopping the tcpdump
h7_tcpdump.terminate() # I then stop the tcpdump on h7 and t1
h1_tcpdump.terminate()

time.sleep(1) #Adding a small delay to make sure tcpdumps are finished.

os.system('mkdir -p ./pcaps_captured_Q1a') # I create a directory to store the captured pcaps
os.system('mv /tmp/*.pcap ./pcaps_captured_Q1a/') # I move the pcaps to the directory
info("***Stopping network\n")
net.stop()


# References:
# http://mininet.org/walkthrough/
# https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py
# https://github.com/mininet/mininet/blob/master/examples/popen.py

