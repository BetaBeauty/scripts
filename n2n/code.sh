
SCRIPTNAME=code.sh
N2N_GIT_VERSION=2.8

code_compile() {
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
}

code_deploy() {
  if [ ! -f "/etc/init.d/n2n" ]; then
    sudo cp -r etc /
    sudo systemctl daemon-reload
    sudo update-rc.d n2n defaults
  fi

  echo "Please edit the configuration file: /etc/default/n2n for your edge node"
}
