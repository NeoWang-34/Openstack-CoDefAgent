from gevent.server import DatagramServer
from multiprocessing import Process
import time


l = []

def deadloop(addr):
	l.append(addr)
	st = time.time()
	while True:
		time.sleep(0.0001)
		cur = time.time()
		if cur - st >= 20:
			break
	l.remove(addr)
 

def reply(req, addr):
	serv.sendto('1'.encode(), addr)
	if addr not in l:
		Process(target=deadloop,args=(addr,)).start()
		


serv = DatagramServer(('0.0.0.0', 2323), reply)
serv.serve_forever()
# import socket
# s = socket.socket(2,2)
# s.bind(('0.0.0.0', 2323))
# print( s.recvfrom(16) )
