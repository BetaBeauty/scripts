
COM=$1

fix_git() {
  cd ~/.vim/bundle/YouCompleteMe
  sed -i 's/\/serving\//\/wlt\//g' `grep "/serving/" -rl YouCompleteMe`
  find . -name '*.pyc' -delete
  cd -
}
