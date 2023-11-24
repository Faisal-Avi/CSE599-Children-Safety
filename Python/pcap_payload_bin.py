from scapy.all import *

def print_payload_binary(packet):
    if Raw in packet:
        payload = packet[Raw].load
        payload_binary = ''.join(format(byte, '08b') for byte in payload)
        print("Payload in Binary: ", payload_binary)
    else:
        print("No payload found.")

def read_pcap(file_path):
    packets = rdpcap(file_path)
    for packet in packets:
        print("Packet summary:")
        print(packet.summary())
        print_payload_binary(packet)
        print("\n")

# Replace 'your_file.pcap' with the path to your pcap file
read_pcap('klcap.pcap')

