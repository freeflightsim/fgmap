#!/usr/bin/php -q
<?php
//#!/usr/bin/php -q

require_once 'mp.core.php';


$errno = "";
$errstr = "";

$pilots = array();


/*
<?xml version="1.0" encoding="UTF-8" ?>
<fg_server pilot_cnt="51">
    <marker callsign="MIA0024" server_ip="LOCAL" model="A330-200" lat="18.043045" lng="-63.113783" alt="31.829342" heading="349.028167724609" pitch="-0.0919775664806366" roll="0.25488743185997" />
    
*/
$xml = '<?xml version="1.0" encoding="UTF-8" ?>';

$ssfp = @fsockopen($url, 5001, $errno, $errstr, 1);

if ($fp) {
    stream_set_timeout($fp, 2);    
	while(feof($fp) == false){
		$line = trim(fgets($fp));
		//echo $line;

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
			
			///print_r($parts);
		}

	}
    fclose ($fp);

	//$data = array('success' => true, 'utc' => time(), 'pilots' => $pilots);
	//print_r($data);
}


echo $errno."=".$errstr."\n";

?>