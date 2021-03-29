_exec() {
  COM=$@
  echo "[running command: ]${COM}"
  eval ${COM}
}

_install_bin() {
  BIN=$@
  echo "Install binary: $@"
  for p in $@; do
    _exec sudo apt install $p
  done
}

echo "Backup the ubuntu source list"
cp /etc/apt/sources.list /etc/apt/sources.list.bak

cat >/etc/apt/sources.list <<EOF
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-proposed main restricted universe multiverse
EOF

_exec sudo apt update
_exec sudo apt upgrade

_install_bin python-dev build-essential
_install_bin make cmake vim git
_install_bin rsync ssh
_install_bin tmux

# https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# sudo add-apt-repository ppa:longsleep/golang-backports
# sudo apt-get install software-properties-common


DIR=ubuntu-server-installer
_ubuntu_server_install() {
  USER=$(whoami)
  sudo -i
  cd /home/${USER}/${DIR}
  echo "Install miniconda3 into /opt"
  bash Miniconda3-latest-Linux-x86_64.sh
}
if [[ ]]
