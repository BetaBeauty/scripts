#!/bin/bash

CONF_PATHS=""
CONF_DESCS=""
CONF_REQ=""

error() {
  MSG=$1
  echo
  if [[ "${MSG}" != "" ]]; then
    echo "[ERROR]: ${MSG}"
  fi

  _usage
  exit -1;
}

_usage() {
cat <<EOF
=======================================================
Usage: collect user configurations
  $0 ${CONF_REQ} [OPTIONS]

  Configuration Files:
    ${CONF_PATHS}

  Options:
    ${CONF_DESCS}

EOF
}

FILES=""
FLAGS=""
REQS=""
OPT_PARSER=""
REQ_PARSER=""

T=$'\t'
LN=$'\n'
PAD="                                        "

_skip() {
  SKS=${1//,/ }
  _old=${FILES}
  FILES=
  for f in ${_old}; do
    flag=0
    for t in ${SKS}; do
      if [[ $f == $t ]]; then
        flag=1
      fi
    done
    if [[ $flag == 0 ]]; then
      FILES="${FILES} $f"
    fi
  done
}

append_usage_path() {
  if [[ ${TARGET} == FILES ]]; then
read -d '' CONF_PATHS <<EOF
    ${CONF_PATHS}
    ${NAME}${PAD:0:$((20 - ${#NAME}))}@${TYPE}${PAD:0:$((10 - ${#TYPE}))}${VALUE}
EOF
  fi
}

append_usage_desc() {
  OPT=""
  if [[ "${NAME}" != "" ]]; then
    OPT="--${NAME}"
  fi
  if [[ "${ALIAS_NAME}" != "" ]]; then
    if [[ "${OPT}" != "" ]]; then
      OPT="${OPT}|"
    fi
    OPT="${OPT}-${ALIAS_NAME}"
  fi
  if [[ ${TYPE} == optional-kv ]]; then
    OPT="${OPT}[=value]"
  fi
read -d '' CONF_DESCS <<EOF
    ${CONF_DESCS}
    ${OPT}${PAD:0:$((18 - ${#OPT}))}${DESC}
EOF
}

append_opt_parser() {
  OPT=""
  if [[ "${NAME}" != "" ]]; then
    if [[ ${TYPE} == optional-kv ]]; then
      OPT="\"--${NAME}=\"*"
    else
      OPT="\"--${NAME}\""
    fi
  fi
  if [[ "${ALIAS_NAME}" != "" ]]; then
    if [[ "${OPT}" != "" ]]; then
      OPT="${OPT}|"
    fi
    if [[ ${TYPE} == optional-kv ]]; then
      OPT="${OPT}\"-${ALIAS_NAME}=\"*"
    else
      OPT="${OPT}\"-${ALIAS_NAME}\""
    fi
  fi
  if [[ "${OPT}" == "" ]]; then
    error "cannot parse the name or alias name"
  fi

  case ${TARGET} in
    FILES) 
      OPT_PARSER="${OPT_PARSER}
        ${OPT}) FILES=\"\${FILES} ${VALUE}\" ;;"
    ;;
    FLAGS) 
      OPT_PARSER="${OPT_PARSER} 
        ${OPT}) FLAGS=\"\${FLAGS} ${VALUE}\" ;;"
    ;;
    *) 
      OPT_PARSER="${OPT_PARSER}
        ${OPT}) ${VALUE} ;;"
    ;;
  esac
}

append_target() {
  case ${TARGET} in
    FILES) 
      FILES="${FILES} ${VALUE}" 
    ;;
    FLAGS) 
      if [[ "${FLAGS}" != "" ]]; then
        FLAGS="${FLAGS} "
      fi
      FLAGS="${FLAGS}${VALUE}" ;;
    *) error "cannot recognized ${TARGET}" ;;
  esac
}

append_req_parser() {
read -d '' REQ_PARSER <<EOF
  ${REQ_PARSER}

  REQ=\$1;
  if [[ "\${REQ}" == "" ]]; then
    error "missing requested parameters - ${NAME}";
  elif [[ \${REQ} =~ ^${PATTERN}$ ]]; then
    if [[ "\${REQS}" != "" ]]; then
      REQS="\${REQS}, ";
    fi;
    REQS="\${REQS}@${NAME}(\${REQ})";
  else
    error "parameter \${REQ} not match pattern \'${PATTERN}\'";
  fi;
  shift;
EOF
}

append_req_conf() {
read -d '' CONF_REQ <<EOF
  ${CONF_REQ} ${DESC}
EOF
}

config() {
  append_usage_path

  case ${TYPE} in
    integral) append_target ;;
    optional|optional-kv) append_usage_desc; append_opt_parser ;;
    request) append_req_conf; append_req_parser ;;
    *) error "cannot recognized config type - ${TYPE}" ;;
  esac

  NAME=
  ALIAS_NAME= # reset alias
}

# === Common Flags ===

  NAME="source"
  TYPE=request
  TARGET=FLAGS
  PATTERN="(.*@.*:|[a-zA-Z0-9_-]+:)?[a-zA-Z0-9~/_\.][a-zA-Z0-9/_\.-]+" # match patten
  DESC="[USER@HOST:]SOURCE_PATH"
config

  NAME="destination"
  TYPE=request
  TARGET=FLAGS
  PATTERN="(.*@.*:|[a-zA-Z0-9_-]+:)?[a-zA-Z0-9~/_\.][a-zA-Z0-9~/_\.-]+" # match patten
  DESC="[USER@HOST:]DEST_PATH"
config

  NAME="help"
  ALIAS_NAME="h"
  TYPE=optional
  TARGET=
  VALUE="error"
  DESC="print help usage"
config

  NAME="skip"
  TYPE=optional-kv
  TARGET=
  VALUE="_skip \${p#*=}"
  DESC="skip some specific configurations, ie. file name, split with comma"
config

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

  NAME="port"
  TYPE=optional-kv
  TARGET=FLAGS
  VALUE="-e \\\"ssh -p \${p#*=}\\\""
  DESC="remote shell port"
config

  NAME="show-progress"
  TYPE=optional
  TARGET=FLAGS
  VALUE='--progress'
  DESC="show rsync progress"
config

  NAME="partial-sync"
  TYPE=optional
  TARGET=FLAGS
  VALUE='--partial'
  DESC="record sync progress counter to network broken and resync"
config

  ALIAS_NAME="P"
  TYPE=optional
  TARGET=FLAGS
  VALUE='--partial --progress'
  DESC="evaluate to --partial-sync --show-progress"
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

  NAME="pip"
  TYPE=integral
  TARGET=FILES
  VALUE=".config/pip"
  DESC="pip profile"
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
  TYPE=integral
  TARGET=FILES
  VALUE=".gitconfig"
  DESC="git config collect"
config

  NAME="npm"
  TYPE=optional
  TARGET=FILES
  VALUE=".npmrc .tern-config"
  DESC="npm config collect"
config

  NAME="ssh"
  TYPE=optional
  TARGET=FILES
  VALUE=".ssh"
  DESC="ssh config, [ATTENTION]: this will copy your private key"
config

# _usage

COM_PARSER="for p in \$@; do
case \$p in ${OPT_PARSER}
  \"-\"*) error \"cannot recognized parameter - \$p\" ;;
  *) 
    if [[ \"\${REQ_PARAMS}\" != \"\" ]]; then
      REQ_PARAMS=\"\${REQ_PARAMS} \";
    fi;
    REQ_PARAMS=\"\${REQ_PARAMS}\$p\" ;;
esac
done;"

eval ${COM_PARSER}

# echo "Command Parser:"
# echo "${COM_PARSER}"
# echo
# echo "Files: ${FILES}"
# echo "Rsync Flags: ${FLAGS}"

REQ_PARSER="
_request_parser() {
  ${REQ_PARSER}

  if [[ \$# != 0 ]]; then
    error \"cannot parse command - \$@\";
  fi;
};

_request_parser ${REQ_PARAMS}
"

# echo "REQ_PARAMS: ${REQ_PARAMS}"
# echo "REQ_PARSER: "
# echo "${REQ_PARSER}"

eval ${REQ_PARSER}

# =========== RSYNC PROGRESS ==========

cat <<EOF
==========================
Print Usage: $0 --help

Collect UNIX Configurations:
  With ${REQS}
  With conf: ${FILES}
  With flag: ${FLAGS}

EOF
echo -n "Do you agree with config above? [Y/N](default N) "
read AGREE

# echo "Collect UNIX configurations:"
# echo "With rsync flag [ ${FLAGS} ] "
# echo "With ${REQS}"
# echo -n ", do you agree?[Y/N](default N) "
# read AGREE
if [[ "${AGREE}" != "Y" && "${AGREE}" != "y" ]]; then
  echo "Stopped collect unix settings with non user-agreement,"
  echo "    refer to help usage with -h for more details."
  exit 0
fi

_try_copy() {
  SRC=$1
  DEST=$2
  FILE=$3

  _com="rsync ${FLAGS} $SRC/$FILE $DEST/"
  echo ${_com}
  eval ${_com}
}

for f in ${FILES}; do
  _try_copy ${REQ_PARAMS} $f
done
