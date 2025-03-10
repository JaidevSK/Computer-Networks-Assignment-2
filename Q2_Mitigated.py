import subprocess
import time
import threading
# This is same as Q2.py. Only, I have done some changes in the configuration of the network to mitigate the attack.
# Previously, I had set the maximum backlog for the SYN queue to 10000, disabled SYN cookies, and set the number of SYN-ACK retries to 1.
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info


class MyTopo(Topo):

    def build(self):

        leftHost = self.addHost('h1')
        rightHost = self.addHost('h2')
        connector = self.addSwitch('s1')

        self.addLink(leftHost, connector, bw=10) 
        self.addLink(connector, rightHost, bw=10)
    

def start_legitimate_traffic(host, server_ip, server_port):
    host.cmd(f'''
                while true; 
                do nc {server_ip} {server_port} <<< "Hello";
                sleep 1; 
                done &
            ''')

    

def start_syn_flood(host, server_ip, server_port):
    host.cmd(f'hping3 -S -p {server_port} --flood --rand-source {server_ip} &')



setLogLevel('info')
topo = MyTopo()
net = Mininet(topo=topo)
net.start()

info("Testing network connectivity\n")
net.pingAll()

h1, h2 = net.get('h1', 'h2')

server_ip = h2.IP()
server_port = 8080

# But now, I have changed the configuration of the network to mitigate the attack.
# I have set the maximum backlog for the SYN queue to 100, enabled SYN cookies, and set the number of SYN-ACK retries to 3.
h2.cmd('sysctl -w net.ipv4.tcp_max_syn_backlog=100')
h2.cmd('sysctl -w net.ipv4.tcp_syncookies=1')
h2.cmd('sysctl -w net.ipv4.tcp_synack_retries=3')

h1.cmd(f'tcpdump -w Q2_attackMitigated.pcap -i {h1.defaultIntf()} tcp &')
time.sleep(1)

legitimate_thread = threading.Thread(target=start_legitimate_traffic, args=(h1, server_ip, server_port))
legitimate_thread.start()

time.sleep(20)
attack_start = time.time()

syn_flood_thread = threading.Thread(target=start_syn_flood, args=(h1, server_ip, server_port))
syn_flood_thread.start()

time.sleep(100)
attack_end = time.time()

h1.cmd('pkill hping3')
syn_flood_thread.join()

time.sleep(20)

h1.cmd('pkill nc')
legitimate_thread.join()

h1.cmd('pkill tcpdump')

net.stop()

# References
# https://www.geeksforgeeks.org/systl-command-in-linux/
# https://nccs.gov.in/public/events/DDoS_Presentation_17092024.pdf
# https://www.geeksforgeeks.org/practical-uses-of-ncnetcat-command-in-linux/
# Other References same as Q1