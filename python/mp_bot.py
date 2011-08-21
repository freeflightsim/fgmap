#!/usr/bin/env python

import os
import sys
import time
import datetime

import threading

import telnetlib
import socket

import operator
import random

import simgear

""" TODO
import ConfigParser
conf = ConfigParser.ConfigParser()
conf.read("../config/config.ini")


MC = None
if conf.get("memcache", "enabled") == "1":
	MC_SERVERS_KEY = conf.get("memcache", "servers_key")
	MC_FLIGHTS_KEY = conf.get("memcache", "flights_key")
	import memcache
	MC = memcache.Client([conf.get("memcache", "url")])	
"""
SITE_DIR = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "../"))

CACHE_DIR = SITE_DIR + "/cache/"
MP_JSON_FILE = CACHE_DIR + 'mp_servers_json.js'
MP_JS_FILE = CACHE_DIR + 'mp_servers_js.js'
MP_FLIGHTS_XML = CACHE_DIR + 'flights.xml'

#print SITE_DIR, CACHE_DIR, MP_JS_FILE
#sys.exit(1)


MAX_MPSERVER_ADDRESS = 5

class MPServers:
	def __init__(self):
		self._addrs = {}
		self._play = {}
		self._dev = {}
		self._fastest = {}
		self._last_dns = None
		
	def last_dns(self):
		return self._last_dns
	
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
		# srtoex_d x is a list of  tuples with (server_name, lag)
		sorted_x = sorted(self._fastest.iteritems(), key=operator.itemgetter(1))
		lenny = len(sorted_x)
		if lenny == 0:
			return
		randy = random.randint(0, 3 if lenny > 4 else lenny - 1)
		server_name =  sorted_x[ randy ][0]
		return self._play[server_name]['ip']

##---------------------------------------------
## Fetch DNS  - THREAD function
def mp_dns_discover(mpServers, last_dns):
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
					print " > " , server_name, port, "\tOK"
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
			mpServers.remove_address(server_name)
	#MC.set("servers", "FOOOOOOOOOOO")
	last_dns = datetime.datetime.now()
	print " DNS Thread Done", last_dns
	
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
		#print  "diff=", delta.seconds, delta.microseconds, ms
		
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

last_dns = None
mpServers = MPServers()
while True:
	if mpServers.has_servers() == 0:
		print "no Servers"
		dns_thread = threading.Thread(	name='mp_dns_discover',
										target=mp_dns_discover, 
										args=(mpServers, last_dns,)
									)
		dns_thread.start()
		time.sleep(5)
	else:
		address = mpServers.random()
		if address == None:
			pass
		else:
			flights = fetch_telnet(address, 5001)
			#print flights
			print " > ", address, len(flights)
			
			if last_dns != None:
				delta = datetime.datetime.now() - last_dns
				print delta
		time.sleep(2)


