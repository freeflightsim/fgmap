#!/usr/bin/env python

DEBUG = True


import os
import sys
import time
import datetime

import threading
import ConfigParser

import telnetlib
import socket

import operator
#import random
from string import Template

try:
	import django.utils.simplejson as json
except:
	import json

import simgear


SITE_DIR = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)), "../")) + "/"


## Init config
conf = ConfigParser.ConfigParser()
config_ini_file = SITE_DIR + "config/config.ini"
if not os.path.exists(config_ini_file):
	print "ERROR:\n  The config file '%s' does not exist\n  Copy the skel file and set params" % config_ini_file
	sys.exit(0)
conf.read(config_ini_file)

MP_REFRESH_RATE = float(conf.get("mp_servers", "refresh_rate")) * 60
FLIGHTS_REFRESH_RATE = float(conf.get("mp_flights", "refresh_rate"))


MC = None
if conf.get("memcache", "enabled") == "1":
	MC_SERVERS_KEY = conf.get("memcache", "servers_key")
	MC_FLIGHTS_KEY = conf.get("memcache", "flights_key")
	import memcache
	MC = memcache.Client([conf.get("memcache", "url")], debug=DEBUG)	


CACHE_DIR = SITE_DIR + "/cache/"
MP_JSON_FILE = CACHE_DIR + 'mp_servers_json.js'
MP_JS_FILE = CACHE_DIR + 'mp_servers_js.js'
MP_FLIGHTS_XML = CACHE_DIR + 'flights.xml'

MAX_MPSERVER_ADDRESS = 5

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class MPServers:
	def __init__(self):
		self._addrs = {}
		self._play = {}
		self._dev = {}
		self._fastest = {}
		self._last_dns = None
		
	def last_dns(self):
		return self._last_dns
	
	def set_last_dns(self):
		self._last_dns = datetime.datetime.now().strftime(DATE_FORMAT)
	
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
				
	def fastest(self):
		# srtoex_d x is a list of  tuples with (server_name, lag)
		sorted_x = sorted(self._fastest.iteritems(), key=operator.itemgetter(1))
		lenny = len(sorted_x)
		if lenny == 0:
			return
		#randy = random.randint(0, 3 if lenny > 4 else lenny - 1)
		server_name =  sorted_x[0][0]
		return self._play[server_name]['ip']

	def get_mp_dic(self):
		dic = {}
		dic['play'] = self._play.values()
		dic['dev'] = self._dev.values()
		dic['last_dns'] = self.last_dns()
		return dic
	
		


##---------------------------------------------
## Find DNS entires  - THREAD function
def mp_dns_discover(mpServers):
	while True:
		if DEBUG:
			print " DNS Thread Starting"
		for no in range(1, MAX_MPSERVER_ADDRESS + 1):
			
			server_name = "mpserver%02d" % no
			server_domain = "%s.flightgear.org" % server_name
			ip_address = dns_lookup_server(server_domain)
			#print "--------------------------------"
			
			if ip_address != None:
				
				#print "dns OK:", server_name, ip_address		
				for port in [5000, 5002]:
					admin_port = port + 1
					lag, info = fetch_telnet(ip_address, admin_port, True) 
					if info != None:
						if DEBUG:
							print " > Found Server " , server_name, port, "\tOK"
						data =  {	'ip': ip_address, 
									'label': "%s:%s" % (server_name, port), 
									'description': "%s:%s" % (server_domain, port), 
									'domain': server_domain,
									'port': admin_port, 
									'lag': lag,
									'info': info
								}
						mpServers.add_mp(server_name, port, data)
					else:
						#print " > " , port, "\tFAILED"
						mpServers.remove_mp(server_name, port)
			else:
				#print "dns Fail:", server_name
				mpServers.remove_address(server_name)
		
		mpServers.set_last_dns()
		
		## Write out to javascript/json files
		dic = mpServers.get_mp_dic()
		json_str = json.dumps(dic)
		
		f = open(MP_JS_FILE, "w")
		f.write("var MP_SERVERS = " + json_str)
		f.close()
		
		f = open(MP_JSON_FILE, "w")
		f.write(json_str)
		f.close()
		
		## Update Memcached
		if MC:
			try:
				MC.set(MC_SERVERS_KEY, json.dumps(dic))
				print "MC OK", MC_SERVERS_KEY
			except:
				#print "MC ERROR", MC_SERVERS_KEY
				pass
		
		if DEBUG:
			print " DNS Thread Done"
		time.sleep(MP_REFRESH_RATE) 
		
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
def fetch_telnet(address, port, ping_mode):

	try:
		start = datetime.datetime.now()
		
		conn = telnetlib.Telnet(address, port, 5)
		data = conn.read_all()
		conn.close()
		
		delta = datetime.datetime.now() - start 
		lag = (delta.seconds * 1000) + (delta.microseconds / 1000)
		#print  "diff=", delta.seconds, delta.microseconds, ms
		
		lines = data.split("\n")
		
		if ping_mode: # MP Ping Mode
			tracked = "@ Not Tracked"
			if lines[2].find("tracked") != -1:
				tracked = lines[2]
				
			if lines[3].find("tracked") != -1:
				tracked = lines[3]
				
				
			pilots = "@ No Pilots"
			if lines[2].find("pilots") != -1:
				pilots = lines[2]
				
			if lines[3].find("pilots") != -1:
				pilots = lines[3]
			
			return lag, {'info': lines[0],
						'version': lines[1],
						'tracked': tracked,
						'pilots': pilots
						}
			
		else: # Flights Mode
			flights = []
			
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
					dic['model'] = os.path.basename(parts[10])[0:-4]
					dic['lat'] = parts[4]
					dic['lon'] = parts[5]
					dic['altitude'] = parts[6]
					
					ob = simgear.euler_get(	float(parts[4]), float(parts[5]), # lat lon
											float(parts[7]), # ox
											float(parts[8]), # oy
											float(parts[9])  # oz
											)
					#print ob
					dic['roll'] = ob.roll
					dic['pitch'] = ob.pitch
					dic['heading'] = ob.heading
					flights.append(dic)
			return lag, flights
				
		
	except 	socket.error as err:
		#print " telnet err=", address, err
		return None,  None

##===============================
def flights_to_xml(flights):
	xml = '<fg_server pilot_cnt="%s">' % len(flights)
	template = Template('<marker callsign="$callsign" server_ip="$server" model="$model" lat="$lat" lng="$lon" alt="$altitude" heading="$heading" pitch="$pitch" roll="$roll"/>')
	for f in flights:
		xml += template.substitute(callsign=f['callsign'], server=f['server'], model=f['model'], 
									lat=f['lat'], lon=f['lon'], altitude=f['altitude'],
									heading=f['heading'], pitch=f['pitch'], roll=f['roll']
									)
	xml += "</fg_server>"
	return xml


##==========================================================================
dns_done = False
mpServers = MPServers()

## create and start DNS thread - runs once atmo
statusThread = threading.Thread(	name='mp_dns_discover',
								target=mp_dns_discover, 
								args=(mpServers, )
							)
statusThread.setDaemon(True)
statusThread.start()

## give status a few seconds to get a few entries
time.sleep(2)

c = 0
## Loop forever and query mp via telnet
while True:
	c = c + 1
	#address = mpServers.random()
	#address = "85.214.37.14" 01
	address = "74.208.230.119" #02
	if address == None:
		pass
	else:
		lag, flights = fetch_telnet(address, 5001, False)
		if DEBUG:
			print " fetch > ", address, statusThread.is_alive(), c
		
		if flights != None:
			f = open(MP_FLIGHTS_XML, "w")
			f.write( flights_to_xml(flights) )
			f.close()
			
			if MC:
				try:
					MC.set(MC_FLIGHTS_KEY, json.dumps(flights))
					MC.set("foo", datetime.datetime.now().strftime(DATE_FORMAT))
					print "MC OK flights", MC_FLIGHTS_KEY
				except:
					pass
					#print "MC FAIL flights"
		"""
		last_dns = mpServers.last_dns()
		if last_dns != None:
			delta = datetime.datetime.now() - last_dns
			print "            ", c, delta, statusThread.is_alive()
			if delta.seconds > 10 and statusThread.is_alive() == False:
				print "START>>>>>>>>>>>>>>>>"
				## BELOW= RuntimeError: thread already started
				statusThread.start()
		"""
	time.sleep(FLIGHTS_REFRESH_RATE)


