#!/bin/sh

DESC='n2n P2P VPN'
NAME=n2n

[ ! -r ./n2n.conf ] && cp ./etc/default/$NAME ./n2n.conf
. ./n2n.conf

DAEMON=$N2N_PATH/edge
DAEMON_ARGS=""             # Arguments to run the daemon with

if [ ! -x "$DAEMON" ]; then
  echo "can not find the binary: edge in path: $N2N_PATH, \
    or you'd better to set customize n2n project compilation path."
  exit 1
fi

if [ -z "$N2N_CONFIG_DONE" ]; then
	echo "Warning: n2n VPN client is not configured, edit config file in n2n.conf." 1>&2
	exit 0
fi

[ -z "$N2N_IP" ] || DAEMON_ARGS="-a $N2N_IP $DAEMON_ARGS"
[ -z "$N2N_MANA_PORT" ] || DAEMON_ARGS="-t $N2N_MANA_PORT $DAEMON_ARGS"
DAEMON_ARGS="-c $N2N_COMMUNITY -l $N2N_SUPERNODE -u $(id -u nobody) \
             -g $(id -u nobody) -f $N2N_VERBOSITY $DAEMON_ARGS"

export N2N_KEY
EXEC_COM="$DAEMON $DAEMON_ARGS"
echo "Exec: $EXEC_COM"
$EXEC_COM || exit 2
