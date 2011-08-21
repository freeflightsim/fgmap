<?php


error_reporting(E_ALL);

date_default_timezone_set('UTC');


//= Max number of dns servers to lookup.
define('MAX_MPSERVER_ADDRESS', 5);

define('MP_REFRESH_RATE', 2000);

//= Site root is the dir above this file
define('SITE_ROOT', realpath( dirname(__FILE__).'/../') );

//= Location of cache directory, must be writable by bot, readable by webserver
define('CACHE_DIR', '../cache/');
define('MP_JSON_FILE', CACHE_DIR.'mp_servers_json.js');
define('MP_JS_FILE', CACHE_DIR.'mp_servers_js.js');
define('MP_FLIGHTS_XML', CACHE_DIR.'flights.xml');




//================================================================
//== Return array of fastest server ip's loaded from cache
function get_fastest(){
	//= load and decode the json data
	$json_str = file_get_contents(MP_JSON_FILE);
	$payload = json_decode($json_str, true);
	//$fastest_scanned = $mp_servers['fastest'];
	//$slowest = count($mp_servers['fastest']) > 5 ? 5 : count($mp_servers['fastest']);
	$foo = array_chunk($payload['fastest'], 5);
	return  $foo[0];
}




//================================================================
//= Spools out $flights array to xml
function flights_to_xml($flights){
	$xml = '<?xml version="1.0" encoding="UTF-8" ?>'."\n";
	$xml .= '<fg_server pilot_cnt="'.count($flights).'">'."\n";
	foreach($flights as $f){
		$xml .= '<marker callsign="'.$f['callsign'].'" server_ip="'.$f['server'].'" ';
		$xml .= 'model="'.$f['model'].'" lat="'.$f['lat'].'" lng="'.$f['lon'].'" ';
		$xml .= 'alt="'.$f['altitude'].'" heading="'.$f['heading'].'" pitch="0" roll="0" />'."\n";
	}
	$xml .= '</fg_server>';
	return $xml;
}




//================================================================
//== Fetches data from telnet admin port, 
//=  returns array of pilots or null is not found
function fetch_mp_telnet($address, $port){
	$errno = '';
	$errstr = '';

	
	$fp = @fsockopen($address, $port, $errno, $errstr, 2);

	if ($fp) {
		stream_set_timeout($fp, 2);  
		$pilots = array();
		while(feof($fp) == false){

			$line = trim(fgets($fp));
			//echo "@".$line;
              /* my($callsign, $server_ip,
                        $x, $y, $z,
                        $lat, $lon, $alt,
                        $ox, $oy, $oz,
                        $model) =
                    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12); */
			if(substr($line, 0, 1) != '#' and $line != ''){ //= Ignore blank and comments Lines
				$parts = explode(' ', $line);
				list($callsign, $server) = explode('@', $parts[0]);
				$pilots[] = array('callsign' => $callsign,
								'server' => $server,
								'lat' => $parts[4], 
								'lon' => $parts[5],
								'altitude' => $parts[6],
								'heading' =>$parts[7],
								'pitch' => '',
								'roll' => '',
								'model' => basename($parts[10], '.xml')
								);
				if($callsign == "MIA0024"){
					print_r($parts);
				}
				
			}

		}
		@fclose ($fp);
		return $pilots;
	}
	@fclose ($fp);
	return null;
}



?>