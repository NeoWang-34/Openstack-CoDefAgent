import socket, time, sys, json
from threading import Thread
from tools.socketTools import *

class Client:

	__clientSocket = None       # socket to connect the server
	__bindedSocket = None       # socket binded in this device for detectors to connect
	__detectorPool = {}         # detector socket pool
	__whitelist = []
	__cuid = None
	ddosTCPBitmask = {0:'Drop_Tcp_Null',1:'Drop_Fin', 3:'Drop_Syn_Fin',\
		 5:'Drop_Fin_Rst', 6:'Drop_Syn_Rst', 8:'Drop_Psh',\
			 32:'Drop_Urg', 41:'Drop_Psh_Fin_Urg'}

	def __init__(self, clientIp, clientPort, serverIp, serverPort):
		# set cuid
		self.__cuid = clientIp + ':' + str(clientPort)
		
		# recovery saved whitelist
		with open('whitelist.json', 'r', encoding='utf8') as fp:
			self.__whitelist = json.load(fp)
		
		# connect to the server
		self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__clientSocket.connect((serverIp, serverPort))
		
		# print whether the client has connect to the server
		print(self.__clientSocket.recv(1024).decode(encoding='utf8') + '\n')

		# bind socket for communicating with detectors
		self.__bindedSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__bindedSocket.bind((clientIp, clientPort))
		self.__bindedSocket.listen(20)
		print("client starts， waiting for detector connecting...\n")

	def acceptDetector(self):
		'''
		create a thread to establish new detector connection
		'''
		while True:
			
			# accept a detector
			detectorSocket, detectorAddr = self.__bindedSocket.accept()
			self.__detectorPool[detectorAddr] = detectorSocket
			print("Detector", detectorAddr[0] + ':' + str(detectorAddr[1]), "connected.\n")
			detectorSocket.sendall("connect client successfully!".encode(encoding='utf8'))

			# create a thread for each detector to receive message
			thread = Thread(target=self.__recvDetectorMsg, args=(detectorSocket, detectorAddr))
			thread.setDaemon(True)
			thread.start()

	def __recvDetectorMsg(self, detectorSocket, detectorAddr):
		'''
		create a thread to receive messages from each detector 
		'''
		while True:
			try:
				msg = recvMsg(detectorSocket)
				if msg == None:
					raise Exception('receive empty message.')
				
				# choose measures according to the message
				if msg['command'] == 'Match':
					if 'bitmask' in msg['condition2']:
						jd = self.__filteringRulesInstall(msg)
					else:
						continue
				else:
					continue
				sendMsg(jd, self.__clientSocket)

			except Exception as e:
				# remove offline detector
				print(e)
				removeSocket(detectorAddr, self.__detectorPool)
				break

	def __filteringRulesInstall(self, recvjd):
		'''
		filtering rules install
		'''
		jd = {}
		head = {}
		head['Type'] = 'PUT'
		head['Code'] = '002'
		head['Uri'] = 'CoDef/FilterRule/cuid=%s' % (self.__cuid)
		#/acl=Drop-Tcp-Null
		data = {}
		ipv4Match = {}
		ipv4Match['srcIp'] = recvjd['srcIp']
		ipv4Match['dstIp'] = recvjd['dstIp']
		tcpMatch = {}
		s = recvjd['condition2']['bitmask'].split()
		tcpMatch['op'] = s[0]
		tcpMatch['bitmask'] = int(s[1])
		data['Ipv4Match'] = ipv4Match
		data['TcpMatch'] = tcpMatch

		if s[0] == 'Match':
			data['Acl'] = self.__handleMatch(int(s[1]))
			data['Action'] = 'DROP'
		else:
			pass

		jd['Head'] = head
		jd['Data'] = data
		return jd
	
	def __handleMatch(self, bitmask):
		if bitmask in self.ddosTCPBitmask:
			return self.ddosTCPBitmask[bitmask]+ '-' + str(time.time())
		return ''

	def recvFromServer(self):
		'''
		receive response messages from server
		'''
		while True:
			try:
				msg = recvMsg(self.__clientSocket)
			except Exception as e:
				print(e)
				break
	
	def handleCMD(self):
		'''
		handle command in Client
		'''
		while True:
			cmd = input()
			if cmd == 'showWhitelist':
				# show the whitelist
				jdstr = json.dumps(self.__whitelist, indent=2, separators=(',', ': '))
				print(jdstr)
			elif cmd == 'addWhitelist':
				# add an ip in whitelist
				newIp = input('new white ip: ')
				if newIp not in self.__whitelist: self.__whitelist.append(newIp)
				with open('whitelist.json','w',encoding='utf8') as fp:
					json.dump(self.__whitelist, fp, ensure_ascii=False, indent=2, separators=(',', ': '))
				print("add white ip '%s' successfully!\n"%(newIp,))
			elif cmd == 'delWhitelist':
				# delte an ip in whitelist
				delIp = input('delete white ip: ')
				if delIp in self.__whitelist:
					self.__whitelist.remove(delIp)
					with open('whitelist.json','w',encoding='utf8') as fp:
						json.dump(self.__whitelist, fp, ensure_ascii=False, indent=2, separators=(',', ': '))
					print("delete white ip '%s' successfully!\n"%(delIp,))
				else:
					print("ip '%s' is not in whitelist!\n"%(delIp,))
			else:
				print('  Sorry, no such cmd!\n' +
						'  usable cmd:\n' +
						'      showWhitelist    -- to show the whitelist\n' +
						'      addWhitelist     -- to add an ip in whitelist\n' +
						'      delWhitelist     -- to delete an ip in whitelist\n')


if __name__ == '__main__':
	
	client = Client(getHostIp(), int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
	Thread(target=client.acceptDetector).start()
	Thread(target=client.recvFromServer).start()
	Thread(target=client.handleCMD).start()