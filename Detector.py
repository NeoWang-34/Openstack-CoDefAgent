import socket, time, sys, json
from threading import Thread
from tools.socketTools import *
from scapy.all import *

class Detector:

	__detectorSocket = None  # socket to connect to the client
	__cnt = {}
	__lastTime = {}
	blacklist = []
	cntTime = 2.0
	cntLimit = 20
	ddosTCPBitmask = [0, 1, 3, 5, 6, 8, 32, 41]

	def __init__(self, clientIp, clientPort):

		# connect to the client
		self.__detectorSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__detectorSocket.connect((clientIp, clientPort))

		# print whether the detector has connect to the client
		print(self.__detectorSocket.recv(1024).decode(encoding='utf8') + '\n')

	def sniffTCP(self):
		'''
		sniff received TCP messages
		'''
		sniff(filter="ip dst %s and tcp" % getHostIp(), prn=self.__handleTCP, count=0)

	def __handleTCP(self, packet):
		'''
		handle received TCP messages\n
		if the count of offensive TCP messages from a host greater than the limit
		in a period of time, we will know we have found DDos messages
		'''
		ip = packet[IP].src
		flags = int(packet[TCP].flags)
		cur = time.time()
		# normal TCP message or IP in blacklist
		if flags not in self.ddosTCPBitmask or ip in self.blacklist: return
		# the first offensive packet from the source host
		# or the offensive packet may not be the offensive packet because of low frequency
		if (ip not in self.__cnt) or (cur - self.__lastTime[ip] > self.cntTime):
			self.__cnt[ip] = 1
			self.__lastTime[ip] = cur
			return
		# count offensive packet
		self.__cnt[ip] += 1
		self.__lastTime[ip] = cur
		if self.__cnt[ip] > self.cntLimit:
			self.blacklist.append(ip)
			with open('/home/ubuntu/msg.txt', 'w') as fp:
				fp.write('检测agent检测到DDos攻击，发送攻击信息...')
			self.__findTCPDDos('Match', packet[IP].src, packet[IP].dst,\
				{'protocol':'TCP'}, packet[TCP].sport, packet[TCP].dport,\
					{'bitmask':'Match %d'%int(packet[TCP].flags)})

	def __findTCPDDos(self, command, srcIp, dstIp, condition1, srcPort, dstPort, condition2):
		msg = {}
		msg['command'] = command
		msg['srcIp'] = srcIp
		msg['dstIp'] = dstIp
		msg['condition1'] = condition1
		msg['srcPort'] = srcPort
		msg['dstPort'] = dstPort
		msg['condition2'] = condition2
		sendMsg(msg, self.__detectorSocket)

if __name__ == '__main__':

	detector = Detector(sys.argv[1],int(sys.argv[2]))
	detector.sniffTCP()
