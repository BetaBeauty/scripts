

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

do_dhcp_setup() {
  # On supernode
  dnf install dhcp-server dhcp-client n2n -y
  systemctl disable dhcpd --now
  supernode -f -l 9090 -v

  # On supernode/one edge
  edge -f -d edge0 -r -a 192.168.1.0 -c foo -k bar -l localhost:9090 -v -A
  cat > /etc/dhcp/dhcpd.conf <<EOF
  subnet 192.168.1.0 netmask 255.255.255.0 {
          range 192.168.1.10 192.168.1.100;
  }
EOF
  dhcpd -f edge0

  # On all other edges
  dnf install dhcp-client n2n -y
  edge -f -d edge0 -r -a dhcp:0.0.0.0 -c foo -k bar -l 116.203.50.42:9090 -v -A -m $(echo $(hostname)|md5sum|sed 's/^\(..\)\(..\)\(..\)\(..\)\(..\).*$/02:\1:\2:\3:\4:\5/') # To get the same MAC address and thus the same IP address every time
  pkill -9 dhclient; dhclient edge0

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
