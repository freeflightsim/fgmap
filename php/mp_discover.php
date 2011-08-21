<?php

/* author: Pete Morgan - pete at freeflightsim for org 

The idea is that this script is run on a cron every few minutes.

It scans a dns range of mpserver 1 to MAX_MPSERVER_ADDRESS below
ie mpserver__.flightear.org, 01 > 

If an ip ddress is found, it then connects on the admin port to check its "there".

The result  are then written out to two files in /cache/ 
 - mp_servers_json.js - as json data records for ajax calls and machine readable
 - mp_servers_js.js - javacript variable ie var MP_SERVER = {data} for inclusion in page load mp_selector

Note there are two flavours of mp..
 - The 'play' on port 5000, admin on 5001 - this is the main ones used my players
 - The 'dev'  on port 5002, admin on 5003 which is rarely available on any server

*/

require_once('mp.core.php');

//= Payload 
//= Note the "mp connection" is port 5000, 5002 = admin ports = mp_connecction + 1
$payload = array('play' => array(), 'dev' => array() );

//= Timing keeps the time it took to connect
$timing = array();

foreach(range(1, MAX_MPSERVER_ADDRESS ) as $no){

	//= Lookup DNS	
	$server_name = sprintf('mpserver%02d', $no);
	$server_domain = $server_name.'.flightgear.org';
	$ip_address = gethostbyname($server_domain);
	echo "--------------------------------\n";
	
	//= We have and address (gethostbyname returns same host if no address)
	if($server_domain != $ip_address){
		
		echo ' + dns OK: '.$server_name.'='.$ip_address."\n";
		foreach(array(5000, 5002) as $port){
			$admin_port = $port + 1;
			//= open and fetch telnet data
			$start = microtime(true);
			$info = fetch_telnet($ip_address, $admin_port); //= use admin port
			$ms = (microtime(true)  - $start) * 1000;

			if( !is_null($info) ){
				echo "   + Telnet $admin_port OK\n";
				$payload[ $port == 5000 ? 'play' : 'dev'] = array(
																	'ip' => $ip_address,
																	'label' => $server_name.':'.$port,
																	'description' => $server_domain.':'.$port,
																	'domain' => $server_domain,
																	'port' => $admin_port,
																	'lag' => $ms
																);
				//= Add play port to timing
				if($port == 5000){
					
					$timing[$ip_address] = $ms;
				}
			}else{
				echo "   - Telnet $admin_port FAIL\n";
			}
		}
	}else{
		echo ' - dns Fail: '.$server_name."\n";
	}
}
//print_r($mp_servers);


//= Sort the timers by fastest
asort($timing, SORT_NUMERIC);
$payload['fastest'] = array_keys($timing);


// write to cache
$json_str = json_encode($payload);
file_put_contents(MP_JSON_FILE , $json_str);
file_put_contents(MP_JS_FILE, 'var MP_SERVERS = '.$json_str);

echo 'Done - '.count($mp_servers['play']).' live servers';

?>