
SCRIPTNAME=service.sh

N2N_GIT_VERSION=2.8

do_install() {
  if [ ! -d ".tmp" ]; then
    mkdir .tmp
  fi

  if [ ! -d ".tmp/n2n" ]; then
    git clone git@github.com:ntop/n2n.git .tmp/n2n || exit 2
    cd .tmp/n2n
    git checkout $N2N_GIT_VERSION
    mkdir build
    cd build && cmake -DCMAKE_INSTALL_PREFIX=/usr .. && sudo make -j8 install
  fi

  if [ ! -f "/etc/init.d/n2n" ]; then
    sudo cp -r etc /
    sudo systemctl daemon-reload
    sudo update-rc.d n2n defaults
  fi

  echo "Please edit the configuration file: /etc/default/n2n for your edge node"
}

force_reload() {
  sudo cp -r etc /
  sudo systemctl daemon-reload
  
  echo "Conf File: /etc/default/n2n has been reloaded, edit it please"
}

do_start() {
  sudo /etc/init.d/n2n restart
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
  reload)
    force_reload
  ;;
  deploy)
    do_install
    do_start
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
Usage: $SCRIPTNAME {install|deploy|reload|start|stop|status}

  deploy    install and start
  install   copy configuration file into /etc and reload the system daemon
  reload    reload conf file for debug usage.
  start|stop|status
EOF

    exit 3
  ;;
esac

exit 0
