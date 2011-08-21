#!/usr/bin/env python

import sys
import time
import datetime

import threading
import telnetlib
import socket

import operator

import simgear

MAX_MPSERVER_ADDRESS = 5

class MPServers:
	def __init__(self):
		self._addrs = {}
		self._play = {}
		self._dev = {}
		self._fastest = {}


	def has_servers(self):
		return len(self._play) != 0

	def add_address(self, server_name, address):
		self._addrs[server_name] = address

	def remove_address(self, server_name):
		if server_name in self._addrs:
			del self._addrs[server_name]

	def add_mp(self, server_name, port, info):
		if port == 5000:
			self._play[server_name] = info
		else:
			self._dev[server_name] = info
		self._fastest[server_name] = info['lag']

	def remove_mp(self, server_name, port):
		if port == 5000:
			if server_name in self._play:
				del self._play[server_name]

			if server_name in self._fastest:
				del self._fastest[server_name]
		else:
			if server_name in self._dev:
				del self._dev[server_name]
				
	def random(self):
		sorted_x = sorted(self._fastest.iteritems(), key=operator.itemgetter(1))
		print sorted_x
##---------------------------------------------
## Fetch DNS from
def mp_dns_discover(mpServers):
	#print "discovermp"
	for no in range(1, MAX_MPSERVER_ADDRESS + 1):
		
		server_name = "mpserver%02d" % no
		server_domain = "%s.flightgear.org" % server_name
		ip_address = dns_lookup_server(server_domain)
		#print "--------------------------------"
		
		if ip_address != None:
			
			#print "dns OK:", server_name, ip_address		
			for port in [5000, 5002]:
				admin_port = port + 1
				lag = fetch_telnet(ip_address, admin_port, ping=True) 
				if lag != None:
					#print " > " , port, "\tOK"
					info =  {	'ip': ip_address, 
								'label': "%s:%s" % (server_name, port), 
								'description': "%s:%s" % (server_domain, port), 
								'domain': server_domain,
								'port': admin_port, 
								'lag': lag
							}
					mpServers.add_mp(server_name, port, info)
				else:
					#print " > " , port, "\tFAILED"
					mpServers.remove_mp(server_name, port)
		else:
			#print "dns Fail:", server_name
			MPServers.remove_address(server_name)

##---------------------------------------------
## Does a DNS loopkup of a server eg mpserver07
def dns_lookup_server(server_domain):

	try:
		addr = socket.gethostbyname(server_domain) #, PORT)		
		return addr

	except socket.gaierror as err:
		#print "  DNS =\t" , server_name, err		
		return None

		
##---------------------------------------------
## Fetch telnet data
def fetch_telnet(address, port, ping=False):

	try:
		start = datetime.datetime.now()
		
		conn = telnetlib.Telnet(address, port, 5)
		data = conn.read_all()
		conn.close()
		
		delta = datetime.datetime.now() - start 
		ms = (delta.seconds * 1000) + (delta.microseconds / 1000)
		print  "diff=", delta.seconds, delta.microseconds, ms
		
		if ping:
			return ms

		flights = []
		lines = data.split("\n")
		for line_raw in lines:
			line = line_raw.strip()
			
			if line.startswith('#') or line == '':
				pass
			else:
				# we got a data line
				parts = line.split(' ')
				callsign, server = parts[0].split('@')
				dic = {}
				dic['callsign'] = callsign
				dic['server'] = server
				dic['lat'] = parts[4]
				dic['lng'] = parts[5]
				dic['altitude'] = parts[6]
				   
				ob = simgear.euler_get(	float(parts[4]), float(parts[5]), # lat lon
										float(parts[7]), # ox
										float(parts[8]), # oy
										float(parts[9])  # oz
										)
				dic['roll'] = ob.roll
				dic['pitch'] = ob.pitch
				dic['heading'] = ob.heading
				flights.append(dic)
		return flights
				
		
	except 	socket.error as err:
		#print " telnet err=", address, err
		return None


mpServers = MPServers()
while True:
	if mpServers.has_servers() == 0:
		print "no Servers"
		dns_thread = threading.Thread(name='mp_dns_discover', target=mp_dns_discover, args=(mpServers,))
		dns_thread.start()
		time.sleep(5)
	else:
		address = mpServers.random()
		print address
		#flights = fetch_telnet(address, 5001)
		#print flights


