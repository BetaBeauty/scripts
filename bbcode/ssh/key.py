from os import path

import paramiko

from bbcode.common import cmd

@cmd.option("--key-file", metavar="FILE",
            default=path.expanduser("~/.ssh/id_rsa"),
            help="rsa private key, by default load path: ~/.ssh/id_rsa")
@cmd.module("ssh.key", as_main=True,
            description="load rsa configuration")
def load_rsa(args):
    return paramiko.RSAKey(filename=args.key_file)

