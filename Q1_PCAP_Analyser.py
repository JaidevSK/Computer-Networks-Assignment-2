import dpkt # I am using the dpkt library to parse the pcap files
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm

def analyze_pcap(pcap_file, output_dir_plots, output_dir_results):
    """
    In this function, we will analyze the pcap file and generate throughput, goodput, and TCP window size plots.
    We will also calculate the total throughput, total goodput, packet loss rate, and maximum window size as required in the question.
    """
    try:
        with open(pcap_file, 'rb') as f: # First we open the pcap file in binary read mode
            pcap = dpkt.pcap.Reader(f) # We then create a pcap reader object
            # We will initialize some lists to store timestamps, packet sizes, TCP payload sizes, and window sizes
            timestamps = []
            packet_sizes = []
            tcp_payload_sizes = []
            tcp_payload_times = []
            seq_numbers = {}
            window_sizes_tcp = []
            seq_nums_ip = {}
            max_window = 0
            time_window = 0.2 # We will use a time window of 0.2 seconds, that is 200 ms. This was giving me the best resolution for the plots

            first_timestamp = None 

            for ts, buf in pcap: # We will iterate over each packet in the pcap file
                if first_timestamp is None: # We will store the first timestamp to calculate relative timestamps
                    first_timestamp = datetime.datetime.utcfromtimestamp(ts) # We will convert the timestamp to a datetime object using the datetime module
                relative_ts = datetime.datetime.utcfromtimestamp(ts) - first_timestamp # We will calculate the relative timestamp with respect to the first timestamp

                rel_ts_seconds = relative_ts.total_seconds() # We will convert the relative timestamp to seconds
                eth = dpkt.ethernet.Ethernet(buf) # Once we have processed the time information, we will parse the Ethernet frame using dpkt
                if isinstance(eth.data, dpkt.ip.IP): # We will check if the Ethernet frame contains an IP packet
                    ip = eth.data # If it is an IP packet, we will extract the IP packet
                    if (ip.src, ip.dst) not in seq_nums_ip: # We will create a set to store the sequence numbers for each IP flow
                        seq_nums_ip[(ip.src, ip.dst)] = set() # We will initialize the set if it does not exist
                    if isinstance(ip.data, dpkt.tcp.TCP): # We will check if the IP packet contains a TCP segment
                        tcp = ip.data # If it is a TCP segment, we will extract the TCP segment
                        timestamps.append(rel_ts_seconds) # We will append the relative timestamp to the timestamps list
                        packet_sizes.append(len(buf)) # We will append the packet size to the packet_sizes list
                        window_sizes_tcp.append(tcp.win) # We will append the TCP window size to the window_sizes list
                        max_window = max(max_window, tcp.win) # We will keep track of the maximum window size
                        if tcp.seq not in seq_nums_ip[(ip.src, ip.dst)]: # We will check if the sequence number is new
                            tcp_payload_sizes.append(len(tcp.data)) # We will append the TCP payload size to the tcp_payload_sizes list
                            tcp_payload_times.append(rel_ts_seconds) # In the case of a new sequence number, we will append the relative timestamp to the tcp_payload_times list
                            seq_nums_ip[(ip.src, ip.dst)].add(tcp.seq) # We will add the sequence number to the set
                        else:
                            tcp_payload_sizes.append(0) # If the sequence number is not new, we will append 0 to the tcp_payload_sizes list
                            tcp_payload_times.append(rel_ts_seconds) # We will append the relative timestamp to the tcp_payload_times list
                    else: # If the IP packet does not contain a TCP segment, we will append 0 to the tcp_payload_sizes list
                        packet_sizes.append(len(buf)) # We will append the packet size to the packet_sizes list
                        tcp_payload_sizes.append(0) # We will append 0 to the tcp_payload_sizes list
                        tcp_payload_times.append(rel_ts_seconds) # We will append the relative timestamp to the tcp_payload_times list
                else: # If the Ethernet frame does not contain an IP packet, we will append 0 to the tcp_payload_sizes list
                    packet_sizes.append(len(buf)) # We will append the packet size to the packet_sizes list
                    tcp_payload_sizes.append(0) # We will append 0 to the tcp_payload_sizes list
                    tcp_payload_times.append(rel_ts_seconds) # We will append the relative timestamp to the tcp_payload_times list


            # We will calculated the throughput

            if not timestamps: # If there are no timestamps, we will return empty lists
                return [], []

            start_time = timestamps[0] # We will get the start time from the timestamps list
            end_time = timestamps[-1] # We will get the end time from the timestamps list
            time_diff = end_time - start_time # The time difference is the difference between the end time and the start time

            if time_diff == 0: # If the time difference is 0, we will return empty lists
                return [], [] 

            num_windows = int(time_diff / time_window) + 1 # We will calculate the number of windows based on the time difference and the time window
            throughput_times = [] # We will initialize a list to store the throughput times
            throughput_values = [] # and throughput values

            for i in range(num_windows): # We will iterate over the number of windows
                window_start = i * time_window # We will calculate the window start time
                window_end = window_start + time_window # and the window end time

                window_sizes = [
                    size * 8
                    for ts, size in zip(timestamps, packet_sizes)
                    if window_start <= ts <= window_end
                ] # We will calculate the throughput for each window

                if window_sizes: # If window sizes exist, we will calculate the throughput
                    throughput = sum(window_sizes) / time_window
                    throughput_times.append(window_start + time_window / 2)
                    throughput_values.append(throughput)

            # Similarly, we will calculate the goodput
            if not tcp_payload_times: # If there are no timestamps, we will return empty lists
                return [], []

            start_time = tcp_payload_times[0] # We will get the start time from the timestamps list
            end_time = tcp_payload_times[-1] # and end time
            time_diff = end_time - start_time # The time difference is the difference between the end time and the start time

            if time_diff == 0: # If the time difference is 0, we will return empty lists
                return [], []

            num_windows = int(time_diff / time_window) + 1 # We will calculate the number of windows based on the time difference and the time window
            goodput_times = []
            goodput_values = []

            for i in range(num_windows): # We will iterate over the number of windows
                window_start = i * time_window # We will calculate the window start time
                window_end = window_start + time_window # and the window end time

                window_sizes = [
                    size * 8
                    for ts, size in zip(tcp_payload_times, tcp_payload_sizes)
                    if window_start <= ts <= window_end
                ] # We will calculate the goodput for each window

                if window_sizes: # If window sizes exist, we will calculate the goodput
                    goodput = sum(window_sizes) / time_window # We will calculate the goodput
                    goodput_times.append(window_start + time_window / 2) # We will append the window start time to the goodput times list
                    goodput_values.append(goodput) # and the goodput to the goodput values list

            total_throughput = sum(packet_sizes) * 8 / (timestamps[-1] - timestamps[0]) if timestamps else 0 # We will calculate the total throughput
            total_goodput = sum(tcp_payload_sizes) * 8 / (timestamps[-1] - timestamps[0]) if timestamps else 0 # and the total goodput

            # Now, we will calculate the packet loss rate
            useful_packets = 0 
            total_packets = 0

            for src, seq_dict in seq_nums_ip.items():
                useful_packets += len(seq_dict) # We will calculate the number of useful packets

            total_packets = len(timestamps) # We will calculate the total number of packets

            packet_loss_rate = (total_packets - useful_packets) / total_packets # We will calculate the packet loss rate as the difference between the total packets and the useful packets divided by the total packets
            # Here, we are assuming that the retransmission packets are not useful and they happen due to packet loss

            # Finally, we will plot the graphs and save the results
            plot_and_save(throughput_times, throughput_values, "Throughput (bits/s)", os.path.basename(pcap_file), output_dir_plots)
            plot_and_save(goodput_times, goodput_values, "Goodput (bits/s)", os.path.basename(pcap_file), output_dir_plots)


            save_results(total_throughput, total_goodput, packet_loss_rate, max_window, os.path.basename(pcap_file), output_dir_results)

            plot_and_save(list(timestamps), list(window_sizes_tcp), "TCP Window Size", os.path.basename(pcap_file), output_dir_plots)


    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def plot_and_save(times, values, title, filename, output_dir):
    """Plots and saves a graph as a PNG file."""
    if not times:
        print(f"No data to plot for {title} in {filename}")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(times, values)
    plt.xlabel("Time (seconds)")
    plt.ylabel(title)
    plt.title(title)
    plt.grid(True, which='both', axis='y')
    plt.minorticks_on()
    plt.tight_layout()

    plot_filename = os.path.splitext(filename)[0] + "_" + title.replace(" ", "_").replace("/", "_") + ".png"
    plt.savefig(os.path.join(output_dir, plot_filename), dpi=300)
    plt.close()

def save_results(total_throughput, total_goodput, packet_loss_rate, max_window, filename, output_dir):
    """Saves results to a text file."""
    results_filename = os.path.splitext(filename)[0] + ".txt"
    filepath = os.path.join(output_dir, results_filename)
    with open(filepath, 'w') as f:
        f.write(f"Total Throughput: {total_throughput:.2f} bits/s\n")
        f.write(f"Total Goodput: {total_goodput:.2f} bits/s\n")
        f.write(f"Packet Loss Rate: {packet_loss_rate:.2%}\n")
        f.write(f"Maximum Window Size: {max_window}\n")

if __name__ == "__main__":
    pcap_dir = "pcaps_captured_Q1d_5"
    output_dir_plots = "plots_obtained_Q1d_5"
    output_dir_results = "results_obtained_Q1d_5"

    os.makedirs(output_dir_plots, exist_ok=True)
    os.makedirs(output_dir_results, exist_ok=True)

    pcap_files = [os.path.join(pcap_dir, filename) for filename in os.listdir(pcap_dir) if filename.endswith(".pcap")]
    for pcap_file in tqdm(pcap_files, desc="Processing PCAP files"):
        analyze_pcap(pcap_file, output_dir_plots, output_dir_results)


# References
# https://kbandla.github.io/dpkt/
# https://dpkt.readthedocs.io/en/latest/
