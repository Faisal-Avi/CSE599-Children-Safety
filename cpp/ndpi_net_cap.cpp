#include <iostream>
#include <pcap.h>
#include <ndpi/ndpi_api.h>
#include <string.h>

using namespace std;

//void packet_callback(u_char* user_data, const struct pcap_pkthdr* pkthdr, const u_char* packet) {
    // Process the captured packet using the NDPI library functions
//}

void packetHandler(u_char* userData, const struct pcap_pkthdr* pkthdr, const u_char* packetData) {
    // Print the packet data
    cout << "Packet captured!" << endl;
    cout << "Packet length: " << pkthdr->len << endl;
    cout << "Number of bytes: " << pkthdr->caplen << endl;
    cout << "Packet data:" << endl;
    for (int i = 0; i < pkthdr->caplen; i++) {
        cout << hex << static_cast<int>(packetData[i]) << " ";
    }
    cout << endl;
}

int main() {

    cout << "Faisal1\n";

    char errbuf[PCAP_ERRBUF_SIZE];

    u_int32_t detection_ticks_resolution = 1000;  // 1 millisecond

    pcap_t* handle;  // Packet capture handle

    struct pcap_pkthdr header;  // Packet header

    const u_char *packet_data; // Packet data

    int packet_length;        // Packet length

    handle = pcap_open_live("ens33", BUFSIZ, 1, 1000, errbuf);

    if (handle == nullptr) {
        cerr << "Couldn't open device: " << errbuf << endl;
        return 1;
    }

    struct ndpi_detection_module_struct* ndpi_struct;

    ndpi_struct = ndpi_init_detection_module(detection_ticks_resolution);

    if (ndpi_struct == nullptr) {
        cout << "Error initializing nDPI library\n";
        return 1;
    }

   // pcap_loop(handle, -1, packet_callback, reinterpret_cast<u_char*>(ndpi_struct));

   // Start capturing packets

    pcap_loop(handle, -1, packetHandler, nullptr);

    if (pcap_loop(handle, -1, packetHandler, nullptr) == -1) {
        cerr << "Error capturing packets: " << pcap_geterr(handle) << endl;
        return 1;
    }

    pcap_close(handle);

    // enable all protocols 
    NDPI_PROTOCOL_BITMASK  all; 
    ndpi_set_protocol_detection_bitmask2(ndpi_struct, &all); 

    // Capture a packet from the file
    packet_data = pcap_next(handle, &header);

    // Obtain the packet length from the packet header
    packet_length = header.len;

    // Pass the packet to nDPI for protocol detection
    ndpi_protocol detected_protocol = ndpi_detection_process_packet(ndpi_struct, packet_data);

    ndpi_exit_detection_module(ndpi_struct);

    cout << "Faisal2\n";

    return 0;
}