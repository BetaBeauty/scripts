from bbcode.common import cmd

from . import key
from . import proxy
from . import local

cmd.module(
    "ssh",
    help="ssh relative tools, like [ssh] command",
    description="""
SSH Tools Module

Support many sub-commands(TODO), like ssh-tunnel. And this tools
    is implemented via third library: paramiko and sshtunnel.
""")
