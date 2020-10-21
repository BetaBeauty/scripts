
SCRIPTNAME=install.sh

do_install() {
  sudo cp -r etc /
  sudo systemctl daemon-reload
}

do_start() {
  sudo /etc/init.d/n2n restart
}

do_deploy() {
  do_install
  do_start
}

do_lookup() {
  sudo /etc/init.d/n2n status
}

do_stop() {
  sudo /etc/init.d/n2n stop
}

case "$1" in
  install)
  do_install
  ;;
  deploy)
  do_deploy
  ;;
  start)
  do_start
  ;;
  stop)
  do_stop
  ;;
  status)
  do_lookup
  ;;
  *)
  cat << EOF
Usage: $SCRIPTNAME {install|deploy|start|stop|status}

  install   copy configuration file into /etc and reload the system daemon
  deploy    install and start
  start|stop|status
EOF

  exit 3
  ;;
esac

exit 0
