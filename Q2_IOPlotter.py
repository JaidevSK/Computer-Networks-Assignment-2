import dpkt
import matplotlib.pyplot as plt
import os
from collections import defaultdict
from tqdm import tqdm

pcap_file = "Q2_attackMitigated.pcap"
output_dir_plots = "io_graphs"
os.makedirs(output_dir_plots, exist_ok=True)
tick_interval=0.1
with open(pcap_file, 'rb') as f: # Open pcap file in binary mode
    pcap = dpkt.pcap.Reader(f) # Read pcap file using dpkt
    # Initialize lists to store timestamps and packet sizes
    timestamps = []
    packet_sizes = []
    first_timestamp = None
    # Iterate over packets in pcap file
    for ts, buf in tqdm(pcap, desc="Processing packets"):  
        if first_timestamp is None: # If this is the first packet, we will store the timestamp
            first_timestamp = ts
        timestamps.append(ts - first_timestamp)
        packet_sizes.append(len(buf))

    # We will group packets by tick interval in time bins
    time_bins = defaultdict(int)
    for ts, size in zip(timestamps, packet_sizes):
        bin_index = int(ts / tick_interval)
        time_bins[bin_index] += size

    # We will now sort the time bins and extract the values for plotting
    bin_times = sorted(time_bins.keys())
    io_values = [time_bins[bin_index] for bin_index in bin_times]
    plot_times = [bin_index * tick_interval for bin_index in bin_times]

    # We will now plot
    plt.figure(figsize=(12, 6))
    plt.plot(plot_times, io_values)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Bytes/Tick")
    plt.title("I/O Graph (Bytes/Tick)")
    plt.grid(True)

    plot_filename = os.path.splitext(os.path.basename(pcap_file))[0] + "_io_graph.png"
    plt.savefig(os.path.join(output_dir_plots, plot_filename), dpi=300)
    plt.close()
