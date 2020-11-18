import routeros_api

def connectRouter(ipaddr):
	'''
	return a router connection entity from its ip address
	'''
	connection = routeros_api.RouterOsApiPool(ipaddr, username='admin', password='')
	router = connection.get_api()
	return router

def getSubnet(router):
	'''
	return a subnet list 
	'''
	addr_list = router.get_binary_resource('/').call('ip/address/print')
	subnet_list = []
	for addr in addr_list:
		if addr['dynamic'] == b'false':
			subnet_list.append(addr['network'].decode())
	# e.g. ['10.0.0.0', '10.0.1.0', '10.0.10.0']
	return subnet_list

def setFilterRule(router, sIp, flags, action, chain):
	'''
	set a filter rule in router which filters tcp messages
	with source Ip address sIp and specific flags 
	'''
	# e.g. setFilterRule(router, '10.0.0.8', 'fin,syn', 'drop', 'input')
	rules = router.get_resource("/ip/firewall/filter")
	rules.add(action=action, chain=chain, protocol="tcp", src_address=sIp, tcp_flags=flags)

def toSubnet(ip, mask):
	'''
	get the subnet to which the ip address belongs from its mask
	'''
	mask //= 8
	tmp = ip.split('.')
	tmp = tmp[:mask] + (4-mask) * ['0']
	return '.'.join(tmp)

if __name__ == "__main__":
	# example
	router_api = connectRouter("192.168.0.158")
	print (router_api)
	print(getSubnet(router_api))
	setFilterRule(router_api, "10.0.0.13", "fin,syn", "drop", "input")

