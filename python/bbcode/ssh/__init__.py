from bbcode.common import cmd

from .base import *
from . import key
from . import tunnel, reverse_tunnel

@cmd.module(
    "ssh", as_main=True,
    help="ssh relative tools, like [ssh] command",
    description="""
SSH Tools Module

Support many sub-commands(TODO), like ssh-tunnel. And this tools
    is implemented via third library: paramiko and sshtunnel.
""")
def main(args):
    user, server = parse_user(args.server)

@cmd.option("-s", "--server",
            help="ssh server address, [user@]hostname[:port]")
@cmd.group("ssh", group_name="secure shell connection")
def group_func(args):
    pass
