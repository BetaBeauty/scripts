from bbcode.common import cmd

from . import key
from . import tunnel, reverse_tunnel

cmd.module(
    "ssh",
    help="ssh relative tools, like [ssh] command",
    description="""
SSH Tools Module

Support many sub-commands(TODO), like ssh-tunnel. And this tools
    is implemented via third library: paramiko and sshtunnel.
""")
