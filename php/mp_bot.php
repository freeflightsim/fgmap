#!/usr/bin/php 
<?php
//#!/usr/bin/php -q

require_once 'mp.core.php';

require_once 'System/Daemon.php';

//= Allowed arguments & their defaults
$runmode = array(
    'no-daemon' => false,
    'help' => false,
    'write-initd' => false,
);
 
//= Scan command line attributes for allowed arguments
foreach ($argv as $k=>$arg) {
    if (substr($arg, 0, 2) == '--' && isset($runmode[substr($arg, 2)])) {
        $runmode[substr($arg, 2)] = true;
    }
}


//System_Daemon::setOption('appName', 'mp_bot');
//System_Daemon::setOption('authorEmail', 'pete@freeflightsim.org');
//System_Daemon::setOption("appDir", dirname(__FILE__));

//$path = System_Daemon::writeAutoRun();
$path  = '';
echo $path."##";
//System_Daemon::log(System_Daemon::LOG_INFO, "Daemon not yet started so ".
//    "this will be written on-screen");

//System_Daemon::start();
//System_Daemon::log(System_Daemon::LOG_INFO, "Daemon: '".
//System_Daemon::getOption("appName").
 //   "' spawned! This will be written to ".
//System_Daemon::getOption("logLocation"));

$mp_servers = get_fastest();
//print_r($mp_servers);


$flights = array();

$RUN = true;
$last = microtime(true);
while($RUN){
	$curr = microtime(true);
	$diff = ($curr - $last ) * 1000;
	//echo " = ".$diff."\n";
	if( $diff > MP_REFRESH_RATE){
		$random = array_rand($mp_servers, 1); //= get one of the servers randomly
		
		$flights = fetch_mp_telnet($mp_servers[$random], 5001);
		//print_r($flights);
		if(!is_null($flights)){
			$xml = flights_to_xml($flights);
			//echo $xml."\n";
			print "DO: ".$mp_servers[$random]." = ".count($flights)."\n";
			file_put_contents(MP_FLIGHTS_XML, $xml);
		}
		$last = microtime(true);
	}
	usleep(200000);
	//usleep(20000);
	//sleep(1);


}

/*
<?xml version="1.0" encoding="UTF-8" ?>
<fg_server pilot_cnt="51">
    <marker callsign="MIA0024" server_ip="LOCAL" model="A330-200" lat="18.043045" lng="-63.113783" alt="31.829342" heading="349.028167724609" pitch="-0.0919775664806366" roll="0.25488743185997" />
    
*/



//System_Daemon::stop();
echo "stopped";
?>