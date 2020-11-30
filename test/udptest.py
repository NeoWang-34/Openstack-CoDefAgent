#!/usr/bin/env python3

import socket
import time
import sys
from threading import Thread

l = [0] * 5
cnt = -1

def udptest(addr, i):

	s = socket.socket(2, 2)
	s.settimeout(10)
	# t = time.time()
	s.sendto(' '.encode(), addr)
	global cnt
	global l
	cnt += 1

	try:
		s.recv(1)
		l[cnt] = 1
		# print( i, ' {:.3f} ms'.format( (time.time() - t) * 1000 ) )
	except:
		# print( i, 'timeout')
		l[cnt] = 0
	

addr = (sys.argv[1], 2323)
while 1:
	l = [0] * 5
	cnt = -1
	pool = [ Thread(target=udptest,args=(addr, i,)) for i in range(5) ]
	for p in pool:
		p.start()
		time.sleep(0.2)
	ans = str(sum(l)/5*100)+'%'
	print('\r'+ans,end='')
	with open('/home/ubuntu/msg.txt', 'w') as fp:
		fp.write(ans)