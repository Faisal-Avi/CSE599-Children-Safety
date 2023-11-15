#include <iostream>
#include <pcap.h>

using namespace std;

static int packetCount = 0;

void packetHandler(u_char *userData, const struct pcap_pkthdr* pkthdr, const u_char* packet) {
  cout << ++packetCount << " packet(s) captured" << endl;
}

void print_packet_info(const u_char *packet, struct pcap_pkthdr packet_header) {
    cout << "Packet capture length:" <<  packet_header.caplen << endl ;
    cout << "Packet total length"<< packet_header.len  << endl ;
}

int main() {
  //char *dev;
  pcap_t *descr;
  char errbuf[PCAP_ERRBUF_SIZE];
  pcap_if_t *alldevs, *dev;

    // Get the list of available devices
  if (pcap_findalldevs(&alldevs, errbuf) == -1) {
        cout << "Error in pcap_findalldevs: " << errbuf << endl;
        return 1;
  }

  // Use the first device found
  dev = alldevs;

  //dev = pcap_lookupdev(errbuf);

  if (dev == NULL) {
      cout << "pcap_lookupdev() failed: " << errbuf << endl;
      return 1;
  }
  
  cout << dev->name;
  cout << "Faisal";
  cout << "\n";

  descr = pcap_open_live(dev->name, BUFSIZ, 0, -1, errbuf);
  if (descr == NULL) {
      cout << "pcap_open_live() failed: " << errbuf << endl;
      return 1;
  }

  if (pcap_loop(descr, 100, packetHandler, NULL) < 0) {
      cout << "pcap_loop() failed: " << pcap_geterr(descr);
      return 1;
  }

  cout << "capture finished" << endl;
  
  return 0;
}