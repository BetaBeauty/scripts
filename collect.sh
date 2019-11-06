if [[ $1 == "--help" || $1 == "-h" ]]; then
  echo "Usage: collect settings in unix"
  echo "  dotcfg.sh [USER@HOST:]path [options]"
  echo ""
  echo "  Settings include:"
  echo "    .profile, .bashrc, .bash_profile, .commacd.bash,"
  echo "    .vimrc, .vundle.vim, .vim, .tmux.conf, aria2.conf"
  echo "  Options format: key=value, where key contains"
  echo "    --help|-h   print help usage"
  echo "    --ssh       collect ssh key information: .ssh"
  echo "    --git       collect git configuration: .gitconfig"
  echo "    --npm       collect nodejs settings: .npmrc, .tern-config"
  echo "    --skip|-s   skip collect specific settings"
  echo ""
  exit 0
fi

FILES=".profile .bashrc .bash_profile .commacd.bash \
.vimrc .vundle.vim .vim .tmux.conf aria2.conf"

_skip() {
  _old=${FILES}
  FILES=
  for f in ${_old}; do
    if [[ $f != $1 ]]; then
      FILES="${FILES} $f"
    fi
  done
}

FLAGS="-avzch -q -P"
for p in $@; do
case $p in 
  "--ssh") FILES="${FILES} .ssh" ;;
  "--git") FILES="${FILES} .gitconfig" ;;
  "--npm") FILES="${FILES} .npmrc .tern-config" ;;
  "--skip="*) _skip ${p#*--skip=} ;;
  "-s="*) _skip ${p#*-s=} ;;
  "--port="*) FLAGS="${FLAGS} -e \"ssh -p ${p#*--port=}\"" ;;
  "-p="*) FLAGS="${FLAGS} -e \"ssh -p ${p#*-p=}\"" ;;
  *) TARGET="$p"; shift ;;
esac
done

TARGET=${TARGET:-./unix}
echo "Collect current unix settings:"
echo "    ${FILES}"
echo -n "into ${TARGET}, do you agree?[Y/N](default yes) "
read AGREE
if [[ "${AGREE}" != "Y" && "${AGREE}" != "y"&& "${AGREE}" != "" ]]; then
  echo "Stopped collect unix settings with non user-agreement,"
  echo "    refer to help usage with -h for more details."
  exit 0
fi

_try_copy() {
  _com="rsync ${FLAGS} $1 ${TARGET}/"
  if [[ -e "$1" ]]; then
    echo ${_com}
    eval ${_com}
  fi
}

for f in ${FILES}; do
  _try_copy ~/$f
done
