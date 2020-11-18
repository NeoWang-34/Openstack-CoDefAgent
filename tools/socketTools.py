import socket
import sys
import json

def getHostIp():
    """
    return host ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def recvMsg(s):
	"""
	receive a json message from the socket s
	"""
	bytes = s.recv(1024)
	msg = bytes.decode(encoding='utf8')
	if len(msg) == 0:
		return None
	else:
		return json.loads(msg)

def sendMsg(msg, s):
	'''
	send a json msg through socket s
	to a specific kind device
	( detector / client / server )
	'''
	jdstr = json.dumps(msg, indent=2, separators=(',', ': '))
	s.sendall(jdstr.encode('utf8'))
	print('send to', s.getpeername()[0] + ':' + str(s.getpeername()[1]), ' ->\n' + jdstr + '\n')
	return jdstr

def removeSocket(addr, socketPool):
	'''
	remove the offline socket through its address
	'''
	if addr in socketPool:
		s = socketPool[addr]
		s.close()
		socketPool.pop(addr)
		print(addr[0] + ':' + str(addr[1]), "is offline.\n")

