
if [ -z "./n2n.conf" ]; then
  . ./n2n.conf
elif [ -z "/etc/default/n2n" ]; then
  . /etc/default/n2n
fi


case $1 in
  -s|--super)
  [ -z "$N2N_MANA_PORT" ] && N2N_MANA_PORT=5645
  ;;
  *)
  [ -z "$N2N_MANA_PORT" ] && N2N_MANA_PORT=5644
  ;;
esac

echo "press Enter for static information query:"
netcat -u localhost $N2N_MANA_PORT
