from gevent.server import DatagramServer
# import time

def reply(req, addr):
	# time_old = int(conn.recv(10))
	# time_now = int(time.time()) - time_old
	# conn.send( str(time_now).encode() )
	# print(addr)
	serv.sendto('1'.encode(), addr)

serv = DatagramServer(('0.0.0.0', 2323), reply)
serv.serve_forever()
# import socket
# s = socket.socket(2,2)
# s.bind(('0.0.0.0', 2323))
# print( s.recvfrom(16) )
