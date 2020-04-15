CONF_PATHS=""
CONF_DESCS=""

_usage() {
cat <<EOF
=======================================================
Usage: collect user configurations
  collect.sh [user@host:|ssh-alias-name:]path [options]

  Configuration Files:
    ${CONF_PATHS}

  Options:
    ${CONF_DESCS}

EOF
}

FILES=""
FLAGS=""

append() {
  type=$1
  shift
  case $type in
    FILES) FILES="${FILES} $@" ;;
    FLAGS) FLAGS="${FLAGS} $@" ;;
    *) echo "cannot recognized $type" ;;
  esac
}

T=$'\t'
PAD="                                        "
append_usage_path() {
  if [[ ${TARGET} == FILES ]]; then
read -d '' CONF_PATHS <<EOF
    ${CONF_PATHS}
    ${NAME}${PAD:0:$((20 - ${#NAME}))}@${TYPE}${PAD:0:$((10 - ${#TYPE}))}${VALUE}
EOF
  fi
}
append_usage_desc() {
read -d '' CONF_DESCS <<EOF
    ${CONF_DESCS}
    --${NAME}${PAD:0:$((18 - ${#NAME}))}${DESC}
EOF
}

COM_PARSE=""
read -d '' COM_PARSE <<EOF
for p in $@; do
case $p in
esac
done
EOF

config() {
  append_usage_path

  case ${TYPE} in
    integral) ;;
    optional) append_usage_desc ;;
  esac
}

# rsync flags

  NAME="default flag"
  TYPE=integral
  TARGET=FLAGS
  VALUE="-avzch"
  DESC="default rsync flags"
config

  NAME="quiet"
  TYPE=optional
  TARGET=FLAGS
  VALUE="-q"
  DESC="rsync quiet flags"
config

# configurations

  NAME="bash profile"
  TYPE=integral
  TARGET=FILES
  VALUE=".profile .bashrc .bash_profile .commacd.bash"
  DESC="default bash profile"
config

  NAME="vim"
  TYPE=integral
  TARGET=FILES
  VALUE=".vimrc .vundle.vim .vim"
  DESC="vim profile and conf"
config

  NAME="tmux"
  TYPE=integral
  TARGET=FILES
  VALUE=".tmux.conf"
  DESC="tmux conf"
config

  NAME="conda"
  TYPE=integral
  TARGET=FILES
  VALUE=".condarc"
  DESC="conda tsinghua source profile"
config

  NAME="aria2"
  TYPE=integral
  TARGET=FILES
  VALUE="aria2.conf"
  DESC="aria2 conf"
config

  NAME="git"
  TYPE=optional
  TARGET=FILES
  VALUE=".gitconfig"
  DESC="git config"
config

  NAME="npm"
  TYPE=optional
  TARGET=FILES
  VALUE=".npmrc .tern-config"
  DESC="npm config"
config

  NAME="ssh"
  TYPE=optional
  TARGET=FILES
  VALUE=".ssh"
  DESC="ssh config, notation: copy your private key"
config


_usage

echo ${FILES}
echo "Rsync Flags: ${FLAGS}"
