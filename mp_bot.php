<?php

error_reporting(E_ALL);

$data = '';
$url='mpserver01.flightgear.org';

echo "#".$url."\n";
$errno = "";
$errstr = "";

$flights = array();
$cols = array('callsign', '1', '2','3','lat','lng','6','7','8','9','model');

$fp = @fsockopen($url, 5001, $errno, $errstr, 1);
if ($fp) {
    stream_set_timeout($fp, 2);    
	while(feof($fp) == false){
		$line = trim(fgets($fp));
		//echo "@".$line;

		
		if(substr($line, 0, 1) != '#'){ //= Ignore comments Lines
			$parts = split(' ', $line);
			$callsign_server = $parts[0];
			$lat = $parts[5];
			$lon = $parts[6];

		}

	}
    fclose ($fp);
}

echo $errno."=".$errstr."\n";

?>