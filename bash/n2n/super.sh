
DESC='n2n P2P VPN'
NAME=n2n

[ ! -r ./n2n.conf ] && cp ./etc/default/$NAME ./n2n.conf
. ./n2n.conf

DAEMON=$N2N_PATH/supernode
DAEMON_ARGS=""             # Arguments to run the daemon with

if [ -z "$N2N_CONFIG_DONE" ]; then
	echo "Warning: n2n VPN super node is not configured, edit config file in n2n.conf." 1>&2
	exit 0
fi

[ ! -x "$N2N_IP_POOLS" ] && DAEMON_ARGS="-a $N2N_IP_POOLS $DAEMON_ARGS"
DAEMON_ARGS="$N2N_VERBOSITY $DAEMON_ARGS"

EXEC_COM="$DAEMON $DAEMON_ARGS"
echo "Exec: $EXEC_COM"
$EXEC_COM || exit 2
