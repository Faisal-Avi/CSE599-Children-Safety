from scapy.all import sniff
import cv2
import numpy as np

def save_image_payload(packet):
    if packet.haslayer('Raw'):
        payload = packet.getlayer('Raw').load

        # Assuming the payload is an image (adjust accordingly)
        img_array = np.frombuffer(payload, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Save the image to a file
        cv2.imwrite('captured_image.jpg', img)

# Sniff packets on the network (adjust the 'iface' parameter to your network interface)
sniff(prn=save_image_payload, store=0, iface='ens33')  # Replace 'eth0' with your actual network interface
