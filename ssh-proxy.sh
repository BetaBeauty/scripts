_help() {
  if [[ $# != 0 ]]; then
    echo "ERROR - $@"
    echo 
  fi

  cat << END_OF_USAGE
Usage -- ssh redirect proxy script
  FORMAT  | ssh-proxy.sh USER HOST [OPTIONAL]
  OPTIONAL: flag=value
    --port|-p       the remote port for redirecting
    --sleep-time|-s the heartbeats of examine interval
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

PORT=8827
SLEEP_TIME=60

SSH_FLAGS=""
for p in $@; do
case $p in 
  "--port="*|"-p="*) PORT=${p#*=} ;;
  "--sleep-time="*|"-s="*) SLEEP_TIME=${p#*=} ;;
  "--local-to-remote="*|"-ltr="*) 
    FLAGS=${p#*=}
    SSH_FLAGS="${SSH_FLAGS} -R ${FLAGS}"
  ;;
  "--remote-to-local="*|"-rtl="*) 
    FLAGS=${p#*=}
    SSH_FLAGS="${SSH_FLAGS} -L ${FLAGS}"
  ;;
  *) _help "unrecognized command: $p" ;;
esac
done

if [[ ${SSH_FLAGS} == "" ]]; then
  SSH_FLAGS="-R ${PORT}:localhost:22"
fi
SSH_FLAGS="${SSH_FLAGS} -o ServerAliveInterval=60"

COM_SSH="ssh -N ${SSH_FLAGS} ${USER}@${HOST} -f"
COM_TEST="nc -z ${HOST} ${PORT}"

echo "PROXY: redirecting local port 22 into ${HOST}:${PORT}"
echo
echo "SSH command:" ${COM_SSH}

# Check the existed connection with ssh
COUNT=`ps -ef | grep "${COM_SSH}" | wc -l`
LOCAL_STATUS=0
if [[ ${COUNT} > 1 ]]; then
  PID=`ps -ef | grep "${COM_SSH}" | head -n 1 | awk '{ print $2 }'`
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
    COUNT=`ps -ef | grep "${COM_SSH}" | wc -l`
    if [[ ${COUNT} > 1 ]]; then
      PID=`ps -ef | grep "${COM_SSH}" | head -n 1 | awk '{ print $2 }'`
      echo "SSH disconnecting: ${PID}"
      kill -9 ${PID}
    fi

    echo "SSH reconnecting..."
    eval ${COM_SSH}
    if [[ $? != 0 ]]; then
      echo "Encountered unknown error"
      exit
    fi

    PID=`ps -ef | grep "${COM_SSH}" | head -n 1 | awk '{ print $2 }'`
    echo "SSH PID: ${PID}"

    LOCAL_STATUS=0
  fi

  sleep ${SLEEP_TIME}
done
