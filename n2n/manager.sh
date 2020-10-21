
[ -z "$N2N_CONF_PATH" ] && N2N_CONF_PATH=./etc/default/n2n

[ -r $N2N_CONF_PATH ] && . $N2N_CONF_PATH

[ -z "$N2N_MANA_PORT" ] && N2N_MANA_PORT=5644

echo "press Enter for static information query:"
netcat -u localhost $N2N_MANA_PORT
