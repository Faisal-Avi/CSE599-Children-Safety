from scapy.all import IP, TCP, Raw, send
import cv2
import numpy as np

def print_payload_binary(packet):
    if Raw in packet:
        payload = packet[Raw].load
        payload_binary = ''.join(format(byte, '08b') for byte in payload)
        return payload_binary
    else:
        print("No payload found.")

image_path = '/home/faisal/Desktop/thesis/V_1mp4_frame1.jpg'
with open(image_path, 'rb') as file:
    img_data = file.read()

# Create a network packet with the image data as a raw payload
packet = IP(dst='192.168.0.103')/TCP(dport=80)/Raw(load=img_data)
print(packet)

payload = print_payload_binary(packet)

raw_payload = packet[Raw].load

# Convert the raw payload to a numpy array
img_array = np.frombuffer(raw_payload, dtype=np.uint8)

# Decode the image using OpenCV
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

# Display or save the image (adjust as needed)
cv2.imwrite('Received_Image.jpg', img)
