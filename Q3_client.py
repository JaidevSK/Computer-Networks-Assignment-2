import socket
import time
import argparse

host = "127.0.0.1"
port = 12345
data_size = 4 * 10000000
transfer_rate = 40000000
duration = 12

parser = argparse.ArgumentParser(description="TCP Client with Nagle and Delayed ACK control.")
parser.add_argument("--nagle", action="store_true", help="enable Nagle's algorithm")
parser.add_argument("--delayed_ack", action="store_true", help="enable Delayed ACK")
parser.add_argument("--config_name", default="Client Test", help="Name of the configuration")
args = parser.parse_args()

results = {
    'packets_sent': 0,
    'packet_loss_count': 0,
    'max_packet_size_sent': 0,
    'sent_times': []
}

nagle_enabled = args.nagle
delayed_ack_enabled = args.delayed_ack

total_bytes_sent = 0
packets_sent = 0
packet_sizes_sent = []
packet_loss_count = 0
sent_times = []
start_time = time.time()

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not nagle_enabled:
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    if not delayed_ack_enabled:
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
    client_socket.connect((host, port))

    sent_data = b'A' * data_size
    sent_index = 0
    while time.time() - start_time < duration and sent_index < data_size:
        send_chunk_size = min(transfer_rate, data_size - sent_index)
        chunk = sent_data[sent_index:sent_index + send_chunk_size]
        client_socket.sendall(chunk)
        total_bytes_sent += len(chunk)
        packets_sent += 1
        packet_sizes_sent.append(len(chunk))
        sent_times.append(time.time())
        sent_index += send_chunk_size
        time.sleep(1)  # enforce the transfer rate.
    client_socket.close()

except ConnectionResetError:
    packet_loss_count += 1
except Exception as e:
    print(f"Client error: {e}")

end_time = time.time()
elapsed_time = end_time - start_time

results['packets_sent'] = packets_sent
results['packet_loss_count'] = packet_loss_count
results['max_packet_size_sent'] = max(packet_sizes_sent) if packet_sizes_sent else 0
results['sent_times'] = sent_times



print(f"Results for {args.config_name}:")
print(f"  Max packet size sent: {results['max_packet_size_sent']} bytes")
print(f"  Packets sent: {results['packets_sent']}")
print(f"  Packet loss count: {results['packet_loss_count']}")
print("-" * 30)
