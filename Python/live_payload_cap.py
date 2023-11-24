from scapy.all import sniff

def packet_callback(packet):
    # Check if the packet has a payload
    if packet.haslayer('Raw'):
        # Extract and print the payload (raw data)
        payload = packet.getlayer('Raw').load
        print("Payload:", payload)

# Sniff packets on the network (adjust the 'iface' parameter to your network interface)
sniff(prn=packet_callback, store=0, iface='ens33')  # Replace 'eth0' with your actual network interface

