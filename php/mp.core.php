<?php


error_reporting(E_ALL);

date_default_timezone_set('UTC');


//= Max number of dns servers to lookup.
define('MAX_MPSERVER_ADDRESS', 10);

//= Site root is the dir above this file
define('SITE_ROOT', realpath( dirname(__FILE__).'/../') );

//= Location of cache directory, must be writable by bot, readable by webserver
define('CACHE_DIR', '../cache/');


//== Fetches data from telnet admin port, 
//=  returns array of pilots or null is not found
function fetch_telnet($address, $port){

	$errno = '';
	$errstr = '';
	$fp = @fsockopen($address, $port, $errno, $errstr, 2);

	if ($fp) {
		stream_set_timeout($fp, 2);    
		while(feof($fp) == false){
			$line = trim(fgets($fp));
			//echo "@".$line;

			if(substr($line, 0, 1) != '#' and $line != ''){ //= Ignore blank and comments Lines
				$parts = explode(' ', $line);
				list($callsign, $server) = explode('@', $parts[0]);
				$pilots[] = array('callsign' => $callsign,
								'server' => $server,
								'lat' => $parts[5], 
								'lon' => $parts[6],
								'alt' => $parts[7],
								'heading' =>$parts[8],
								'pitch' => '',
								'roll' => ''
								);
				
				//print_r($parts);
			}

		}
		fclose ($fp);
		//print_r($pilots);
		return $pilots;
	}
	return null;
}

?>