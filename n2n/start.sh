

do_install() {
  git clone git@github.com:ntop/n2n.git
  cd n2n
  ./autogen.sh
  ./configure
  make -j8
  make install
}

do_start_supernode() {
  supernode -v
}

do_look_up_network() {
  netcat -u localhost 5645
}

do_start_edgenode() {
  edge conf.edge
}

case "$1" in
  install)
  do_install
  ;;
  start_super)
  do_start_supernode
  ;;
  start_edge)
  do_start_edgenode
  ;;
  lookup)
  do_look_up_network
  ;;
  *)
  echo "Usage: $SCRIPTNAME {install|start_super|start_edge|lookup}" >& 2  
  exit 3
  ;;

esac

exit 0
