#!/bin/sh

[ -z "$N2N_PATH" ] && N2N_PATH=/usr/sbin

DESC='n2n P2P VPN'
NAME=n2n
DAEMON=$N2N_PATH/edge
DAEMON_ARGS=""             # Arguments to run the daemon with

if [ ! -x "$DAEMON" ]; then
  echo "cannot find the binary: edge"
  exit 1
fi

[ -r ./etc/default/$NAME ] && . ./etc/default/$NAME

if [ -z "$N2N_EDGE_CONFIG_DONE" ]; then
	echo "Warning: n2n VPN client is not configured, edit config file in etc/default/$NAME." 1>&2
	exit 0
fi

if [ ! -z "$N2N_IP" ]; then
  DAEMON_ARGS="-a $N2N_IP"
fi

if [ ! -z "$N2N_MANA_PORT" ]; then
  DAEMON_ARGS="-t $N2N_MANA_PORT $DAEMON_ARGS"
fi

export N2N_KEY
$DAEMON -c $N2N_COMMUNITY -l $N2N_SUPERNODE -u $(id -u nobody) -g $(id -g nobody) \
  -f $DAEMON_ARGS || return 2
