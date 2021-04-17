sudo apt install python3 python-dev build-essential
sudo apt install git
# sudo apt install vim
sudo apt install make cmake

cat >$HOME/.bashrc <<EOF
export PYTHONPATH=$HOME/scripts:$PYTHONPATH
EOF

