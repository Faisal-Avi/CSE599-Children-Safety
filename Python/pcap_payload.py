from scapy.all import *

def print_payload(packet):
    if Raw in packet:
        payload = packet[Raw].load
        print("Payload: ", payload)
    else:
        print("No payload found.")

def read_pcap(file_path):
    packets = rdpcap(file_path)
    for packet in packets:
        print("Packet summary:")
        print(packet.summary())
        print_payload(packet)
        print("\n")

# Replace 'your_file.pcap' with the path to your pcap file
read_pcap('klcap.pcap')

