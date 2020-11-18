#!/usr/bin/env python3

import socket
import time
import sys
from threading import Thread

l = [0] * 100
cnt = 0

def udptest(addr, i):
	# addr = ('121.42.185.92', 2323)

	s = socket.socket(2, 2)
	s.settimeout(10)
	t = time.time()
	s.sendto(' '.encode(), addr)
	global cnt
	global l
	if cnt < 100:	cnt += 1
	try:
		s.recv(1)
		l[i] = 1
		# print( i, ' {:.3f} ms'.format( (time.time() - t) * 1000 ) )
	except:
		# print( i, 'timeout')
		l[i] = 0
	finally:
		print(sum(l)/cnt*100,'%')

# [ udptest(i) for i in range(10) ]
# exit()

addr = (sys.argv[1], 2323)
while 1:
	pool = [ Thread(target=udptest,args=(addr, i,)) for i in range(100) ]
	for p in pool:
		p.start()
		time.sleep(0.1)
