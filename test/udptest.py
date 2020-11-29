#!/usr/bin/env python3

import socket
import time
import sys
from threading import Thread

l = [0] * 100
cnt = -1
tot = 0

def udptest(addr, i):

	s = socket.socket(2, 2)
	s.settimeout(10)
	# t = time.time()
	s.sendto(' '.encode(), addr)
	global cnt
	global tot
	global l
	cnt = (cnt+1)%100
	if tot < 100:	tot += 1

	try:
		s.recv(1)
		l[cnt] = 1
		# print( i, ' {:.3f} ms'.format( (time.time() - t) * 1000 ) )
	except:
		# print( i, 'timeout')
		l[cnt] = 0
	finally:
		print(sum(l)/tot*100,'%')
		#print(sum(l),tot)

# [ udptest(i) for i in range(10) ]
# exit()

addr = (sys.argv[1], 2323)
st = time.time()
while 1:
	cur = time.time()
	if cur - st >= 20:
		break
	pool = [ Thread(target=udptest,args=(addr, i,)) for i in range(50) ]
	for p in pool:
		p.start()
		time.sleep(0.1)
