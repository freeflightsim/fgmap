#!/usr/bin/env python

"""
pete@freeflightsim.org 

Discovers MP servers from DNS, then connects to them to chck if online

This writes the servers out to mp_servers.js

"""

# Max number of servers to look
MAX_MPSERVER_ADDRESS = 20

import socket
import telnetlib

try:
	import django.utils.simplejson as json
except:
	import json


## Does a DNS loopkup of a server eg mpserver07
def lookup_server(server_domain):

	try:
		addr = socket.gethostbyname(server_domain) #, PORT)		
		return addr

	except socket.gaierror as err:
		print "  DNS =\t" , server_name, err		
		return None
	


## Telnet connections
def get_telnet(address, port):
	try:
		conn = telnetlib.Telnet(address, port, 5)
		data = conn.read_all()
		conn.close()		
		return True
		
	except 	socket.error as err:
		#print " telnet err=", address, err
		return None
		






## Payload 
## Not the "mp connectioN" is port 5000, 5002 = admin -1
mp_servers = {'play': [], 'dev': []}

## Loop range and lookup servers
for no in range(1, MAX_MPSERVER_ADDRESS + 1):
	
	server_name = "mpserver%02d" % no
	server_domain = "%s.flightgear.org" % server_name
	ip_address = lookup_server(server_domain)
	print "--------------------------------"
	
	if ip_address != None:
		
		print "dns OK:", server_name, ip_address		
		for port in [5001, 5003]:
			info = get_telnet(ip_address, port) # server_name + ".flightgear.org")
			if info != None:
				print " > " , port, "\tOK"
				mp_servers['play' if port == 5001 else 'dev'].append( {
											'ip': ip_address, 
											'label': "%s:%s" % (server_name, port -1), 
											'description': "%s:%s" % (server_domain, port -1), 
											'domain': server_domain,
											'port': port
										})
			else:
				print " > " , port, "\tFAILED"
	else:
		print "dns Fail:", server_name


#print "DONE", mp_servers

## write to mp_servers.js
f = open("mp_servers.js", "w")
js_str = "var MP_SERVERS = " + json.dumps( mp_servers, ensure_ascii=True, )
f.write(js_str)
f.close()
#print js_str

print "mp_servers.js writtern.. done :-)"








