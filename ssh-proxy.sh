_help() {
  if [[ $# != 0 ]]; then
    echo "ERROR - $@"
    echo 
  fi

  cat << END_OF_USAGE
Usage -- ssh redirect proxy script
  FORMAT  | ssh-proxy.sh USER HOST [OPTIONAL]
  OPTIONAL: flag=value
    --remote-to-local|-rtl    redirect remote port into local.

    --port|-p       the remote port for redirecting.
    --visibility|-v the visibility of remote port, * or localhost etc.
                    * by default.

    --local-host|-lh  the local host ip, 127.0.0.1 by default.
    --local-port|-lp  the local host port, 22 by default.

    --sleep-time|-s   the heartbeats of examine interval.
    --help|-h         this help usage.
END_OF_USAGE

  exit
}

USER=$1
shift
if [[ ${USER} == "" ]]; then
  _help "user is empty"
fi
HOST=$1
shift
if [[ ${HOST} == "" ]]; then
  _help "host is empty"
fi

# Format: DIRECTION VISIBLITY:REMOTE-PORT:LOCAL-HOST:LOCAL-PORT
DIRECTION="-R"
VISIBLITY="*"
PORT=8827
LOCAL_HOST="localhost"
LOCAL_PORT=22

SLEEP_TIME=60

for p in $@; do
case $p in 
  "--port="*|"-p="*) PORT=${p#*=} ;;
  "--visiblity="*|"-v="*) VISIBLITY=${p#*=} ;;

  "--local-to-remote"|"-ltr") DIRECTION="-R" ;;
  "--remote-to-local"|"-rtl") DIRECTION="-L" ;;
  "--local-host="*|"-lh="*) LOCAL_HOST=${p#*=} ;;
  "--local-port="*|"-lp="*) LOCAL_PORT=${p#*=} ;;

  "--sleep-time="*|"-s="*) SLEEP_TIME=${p#*=} ;;
  *) _help "unrecognized command: $p" ;;
esac
done

SSH_FLAGS="-N ${DIRECTION} ${VISIBLITY}:${PORT}:${LOCAL_HOST}:${LOCAL_PORT}"
SSH_FLAGS="${SSH_FLAGS} -o ServerAliveInterval=60"

COM_SSH="ssh ${SSH_FLAGS} ${USER}@${HOST} -f"
COM_TEST="nc -z ${HOST} ${PORT}"

echo "PROXY: redirecting local port 22 into ${HOST}:${PORT}"
echo
echo "SSH command:" ${COM_SSH}

# Check the existed connection with ssh
COUNT=`ps -ef | grep -F "${COM_SSH}" | wc -l`
LOCAL_STATUS=0
if [[ ${COUNT} > 1 ]]; then
  PID=`ps -ef | grep -F "${COM_SSH}" | head -n 1 | awk '{ print $2 }'`
  echo "SSH PID: ${PID}"
else
  LOCAL_STATUS=1
fi

while true; do
  eval ${COM_TEST}
  REMOTE_STATUS=$?
  if [[ ${REMOTE_STATUS} == 0 ]] && [[ ${LOCAL_STATUS} == 0 ]]; then
    echo -e "\033[32m[`date`] Status: connected \033[0m"
  else
    echo -e "\033[31m[`date`] Status: disconnected \033[0m"

    # Kill all currently connection instance 
    COUNT=`ps -ef | grep -F "${COM_SSH}" | wc -l`
    if [[ ${COUNT} > 1 ]]; then
      PID=`ps -ef | grep -F "${COM_SSH}" | head -n 1 | awk '{ print $2 }'`
      echo "SSH disconnecting: ${PID}"
      kill -9 ${PID}
    fi

    echo -e "\033[32m[`date`] SSH reconnecting... \033[0m"
    eval ${COM_SSH}
    while [[ $? != 0 ]]; do
      echo "Encountered unknown error"
      sleep 60
      echo -e "\033[32m[`date`] Retrying... \033[0m"
      eval ${COM_SSH}
    done

    PID=`ps -ef | grep -F "${COM_SSH}" | head -n 1 | awk '{ print $2 }'`
    echo "SSH PID: ${PID}"

    LOCAL_STATUS=0
  fi

  sleep ${SLEEP_TIME}
done
