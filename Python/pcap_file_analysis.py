from scapy.all import *

def process_packet(packet):
    # Your packet processing logic here
    print(packet.summary())

def read_pcap(file_path):
    packets = rdpcap(file_path)
    for packet in packets:
        process_packet(packet)

# Replace 'your_file.pcap' with the path to your pcap file
read_pcap('klcap.pcap')
