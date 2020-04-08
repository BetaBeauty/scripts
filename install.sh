
COM="$1"

fix_git() {
  INAME=$(whoami)
  cd ~/.vim/bundle/YouCompleteMe
  sed -i "s/\/serving\//\/${INAME}\//g" `grep "/serving/" -rl YouCompleteMe`
  find . -name '*.pyc' -delete
  cd -
}

if [[ $COM == "--fix-git" ]]; then
  fix_git
fi
