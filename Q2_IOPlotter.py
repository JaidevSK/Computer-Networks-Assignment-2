import dpkt # Import dpkt module for reading pcap files
import matplotlib.pyplot as plt
import os
from collections import defaultdict
from tqdm import tqdm

pcap_file = "Q2_attackMitigated.pcap" # Path to pcap file. I changed the name of the pcap file to Q2_attack.pcap in order to plot the graph for the attack.
output_dir_plots = "io_graphs"
os.makedirs(output_dir_plots, exist_ok=True)
tick_interval=0.1 # This is the bin size in seconds
with open(pcap_file, 'rb') as f: # Open pcap file in binary mode
    pcap = dpkt.pcap.Reader(f) # Read pcap file using dpkt
    # Initialize lists to store timestamps and packet sizes
    timestamps = []
    packet_sizes = []
    first_timestamp = None
    for ts, buf in tqdm(pcap, desc="Processing packets"):   # I then iterated over the packets in the pcap file
        if first_timestamp is None: # If this is the first packet, we will store the timestamp
            first_timestamp = ts 
        timestamps.append(ts - first_timestamp) # We will store the timestamp relative to the first packet
        packet_sizes.append(len(buf)) # We will store the packet size

    time_bins = defaultdict(int) # We will now create a dictionary to store the time bins
    for ts, size in zip(timestamps, packet_sizes): # We will iterate over the timestamps and packet sizes
        bin_index = int(ts / tick_interval) # We will calculate the bin index
        time_bins[bin_index] += size # We will add the packet size to the corresponding bin

    bin_times = sorted(time_bins.keys()) # We will sort the bin times
    io_values = [time_bins[bin_index] for bin_index in bin_times] # We will store the I/O values
    plot_times = [bin_index * tick_interval for bin_index in bin_times] # We will store the plot times

    # We will now plot and save the I/O graph
    plt.figure(figsize=(12, 6))
    plt.plot(plot_times, io_values)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Bytes/Tick")
    plt.title("I/O Graph (Bytes/Tick)")
    plt.grid(True)

    plot_filename = os.path.splitext(os.path.basename(pcap_file))[0] + "_io_graph.png"
    plt.savefig(os.path.join(output_dir_plots, plot_filename), dpi=300)
    plt.close()
