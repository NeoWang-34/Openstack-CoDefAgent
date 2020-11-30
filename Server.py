import socket, time, sys, json, routeros_api
from threading import Thread
from tools.socketTools import *
from tools.routerTools import *

class Server:

	__serverSocket = None     # socket binded in server for clients to connect
	__clientPool = {}         # client socket pool
	ddosTCPBitmask = {0:'',1:'fin', 3:'syn,fin',\
		 5:'fin,rst', 6:'syn,rst', 8:'psh',\
			 32:'urg', 41:'psh,fin,urg'}
	routerIP = []
	routers = {}
	subnets = {}

	def __init__(self, serverIp, serverPort,routerIP):
		self.routerIP = routerIP
		self.getNetworkInformation()
		# bind socket for communicating with clients
		self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__serverSocket.bind((serverIp, serverPort))
		self.__serverSocket.listen(20)
		print("server start，wait for client connecting...\n")

	def getNetworkInformation(self):
		routers = {}
		subnets = {}
		for ip in self.routerIP:
			self.routers[ip] = connectRouter(ip)
			subnetlist = getSubnet(self.routers[ip])
			for subnet in subnetlist:
				self.subnets[subnet] = ip

	def acceptClient(self):
		'''
		establish new client connection
		'''
		while True:
			clientSocket, clientAddr = self.__serverSocket .accept()
			print("Client " + clientAddr[0] + ':' + str(clientAddr[1]) + " connected.\n")
			self.__clientPool[clientAddr] = clientSocket
			clientSocket.sendall("connect server successfully!".encode(encoding='utf8'))

			# create an independent thread for each client to receive messages
			thread = Thread(target=self.__recvClientMsg, args=(clientSocket, clientAddr))
			thread.setDaemon(True)
			thread.start()

	def __recvClientMsg(self, clientSocket, clientAddr):
		'''
		create a thread to receive messages from each client
		'''
		while True:
			try:
				msg = recvMsg(clientSocket)
				if msg == None:
					raise Exception('receive empty message.')

				# process according to the message
				if( msg['Data']['Action'] == 'DROP' ):
					jd = self.__filteringRulesInstall(msg)
				else:
					continue
				sendMsg(jd, clientSocket)
			except Exception as e:
				# remove offline client
				print(e)
				removeSocket(clientAddr, self.__clientPool)
				break

	def __filteringRulesInstall(self, recvjd):
		with open('/home/ubuntu/msg.txt', 'w') as fp:
			fp.write('服务器agent收到缓解请求，执行缓解响应...')
		srcIp = recvjd['Data']['Ipv4Match']['srcIp']
		dstIp = recvjd['Data']['Ipv4Match']['dstIp']
		flags = recvjd['Data']['TcpMatch']['bitmask']
		dstRouter = self.routers[ self.subnets[toSubnet(dstIp, 24)] ]
		srcRouter = self.routers[ self.subnets[toSubnet(srcIp, 24)] ]
		time.sleep(3)
		with open('/home/ubuntu/msg.txt', 'w') as fp:
			fp.write('部署末端路由器进行流量清洗过滤...')
		setFilterRule(dstRouter, srcIp, self.ddosTCPBitmask[flags], "drop", "forward")
		time.sleep(3)
		with open('/home/ubuntu/msg.txt', 'w') as fp:
			fp.write('部署上游路由器协同进行流量清洗过滤...')
		setFilterRule(srcRouter, srcIp, self.ddosTCPBitmask[flags], "drop", "forward")
		jd = {}
		head = {}
		head['Type'] = 'CREATED'
		head['Code'] = '201'
		head['Uri']  = recvjd['Head']['Uri'] + '/acl=' +recvjd['Data']['Acl']
		jd['Head'] = head
		return jd

if __name__ == '__main__':

	routerIP = sys.argv[2:]
	server = Server(getHostIp(), int(sys.argv[1]), routerIP)
	Thread(target=server.acceptClient).start()
