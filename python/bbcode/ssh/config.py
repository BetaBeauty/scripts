from os import path
import getpass

import paramiko

from bbcode.common import cmd

from .base import DEFAULT_SSH_DIRECTORY

SSH_CONFIG_FILE = path.join(DEFAULT_SSH_DIRECTORY, 'config')

def ssh_config(hostname,
               config_file=SSH_CONFIG_FILE,
               username=None,
               private_key=None,
               port=None):
    ssh_config = paramiko.SSHConfig()
    with open(path.expanduser(config_file), "r") as f:
        ssh_config.parse(f)

    info = ssh_config.lookup(hostname)
    username = username or info.get("user", getpass.getuser())
    private_key = private_key or info.get("identityfile", [None])[0]
    host = info.get("hostname", hostname)
    port = port or info.get("port", 22)

    return (
        host,
        username,
        private_key,
        int(port),
    )

