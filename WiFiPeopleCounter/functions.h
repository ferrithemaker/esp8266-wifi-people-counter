// Expose Espressif SDK functionality

extern "C" {
#include "user_interface.h"
  typedef void (*freedom_outside_cb_t)(uint8 status);
  int  wifi_register_send_pkt_freedom_cb(freedom_outside_cb_t cb);
  void wifi_unregister_send_pkt_freedom_cb(void);
  int  wifi_send_pkt_freedom(uint8 *buf, int len, bool sys_seq);
}

#include <ESP8266WiFi.h>
#include "./structures.h"

#define MAX_APS_TRACKED 100
#define MAX_CLIENTS_TRACKED 200

int aps_known_count = 0;                                  // Number of known APs
int nothing_new = 0;
int clients_known_count = 0;                              // Number of known CLIENTs
int foundMAC;

void promisc_cb(uint8_t *buf, uint16_t len)
{
  signed potencia;
  if (len == 12) {
    struct RxControl *sniffer = (struct RxControl*) buf;
    potencia = sniffer->rssi;
  } else if (len == 128) {
    struct sniffer_buf2 *sniffer = (struct sniffer_buf2*) buf;
    struct beaconinfo beacon = parse_beacon(sniffer->buf, 112, sniffer->rx_ctrl.rssi);
    potencia = sniffer->rx_ctrl.rssi;
  } else {
    struct sniffer_buf *sniffer = (struct sniffer_buf*) buf;
    potencia = sniffer->rx_ctrl.rssi;
  }
  char currentMAC[10];
  
  // Position 12 in the array is where the packet type number is located
  // For info on the different packet type numbers check:
  // https://stackoverflow.com/questions/12407145/interpreting-frame-control-bytes-in-802-11-wireshark-trace
  // https://supportforums.cisco.com/document/52391/80211-frames-starter-guide-learn-wireless-sniffer-traces
  // https://ilovewifi.blogspot.mx/2012/07/80211-frame-types.html

  
  if((buf[12]==0x88)||(buf[12]==0x40)||(buf[12]==0x94)||(buf[12]==0xa4)||(buf[12]==0xb4)||(buf[12]==0x08))
  {
    //Serial.printf("%02x\n",buf[12]);
    // if(buf[12]==0x40) Serial.printf("Disconnected: ");
    // if(buf[12]==0x08) Serial.printf("Data: ");
    // if(buf[12]==0x88) Serial.printf("QOS: ");
    // Origin MAC address starts at byte 22
    // Print MAC address

    // convert *buf (only MAC) to string

    sprintf(currentMAC,"%02x%02x%02x%02x%02x",buf[22],buf[23],buf[24],buf[25],buf[26]);
    //Serial.print("Current MAC:");
    //Serial.println(currentMAC);
    for (int i=0;i<MAXlist;i++) {
      foundMAC = 1;
      for (int bytepos=0;bytepos<10;bytepos++) {
        if (currentMAC[bytepos] != lastMACs[i][bytepos]) {
          foundMAC = 0;
        }       
      }
      if (foundMAC == 1) {
          //Serial.print("FOUND RECORDED MAC AT ");
          //Serial.println(i);
          break;  
      }
    }
    if (!foundMAC && int8_t(buf[0])>SIGNAL_THRESHOLD) {
      strncpy(lastMACs[MACindex],currentMAC,10);
      Serial.print("NEW MAC WITH GOOD SIGNAL DETECTED: ");
      Serial.println(currentMAC);
      MACindex++;
    }
    if (MACindex == MAXlist) {
      Serial.println("BUFFER FULL: READY TO START SENDING MACs INFORMATION TO MQTT SERVER");
      for (int i=0;i<MAXlist;i++) {
        for (int i2=0;i2<10;i2++) {
          Serial.print(lastMACs[i][i2]);
        }
        Serial.println();
      }
      MACindex = 0;
      // stop sniffing and start sending data (change WiFi configuration)
      sniffing = false;
    }  
   
    // Enable this lines if you want to scan for a specific MAC address
    // Specify desired MAC address on line 10 of structures.h
    /*
    int same = 1;
    for(int i=0;i<6;i++)
    {
      if(buf[22+i]!=desired[i])
      {
        same=0;
        break;
      }
    }
    if(same)
    {
      Serial.println("MAC found!");
    }
    //different device
    else
    {
      Serial.println(currentMAC);
    }
   */
  }
}
