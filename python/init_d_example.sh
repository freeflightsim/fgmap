#! /bin/sh

### BEGIN INIT INFO
# Provides:          YOURPROJECT
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts YOURPROJECT
# Description:       starts YOURPROJECT using start-stop-daemon
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=""
DAEMON_OPTS='/home/ffs/public_html/fgmap-github/python/mp_bot.py'
NAME=mp_bot
DESC=FlightGear Multiplayer Bot
PIDFILE="/var/run/${NAME}.pid"
QUIET="--quiet"
START_OPTS="--start ${QUIET} --background --make-pidfile --pidfile ${PIDFILE} --exec ${DAEMON} ${DAEMON_OPTS}"
STOP_OPTS="--stop --pidfile ${PIDFILE}"

test -x $DAEMON || exit 0

set -e

case "$1" in
  start)
	echo -n "Starting $DESC: "
	start-stop-daemon $START_OPTS
	echo "$NAME."
	;;
  stop)
	echo -n "Stopping $DESC: "
	start-stop-daemon $STOP_OPTS
	echo "$NAME."
	;;
  restart|force-reload)
	echo -n "Restarting $DESC: "
	start-stop-daemon $STOP_OPTS
	sleep 1
	start-stop-daemon $START_OPTS
	echo "$NAME."
	;;
  *)
	N=/etc/init.d/$NAME
	echo "Usage: $N {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac

exit 0