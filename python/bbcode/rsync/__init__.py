from . import sync

from bbcode.common import cmd

cmd.module("rsync",
            help="rsync helper tools",
            description="""
rSync Helper Tools

wrapper rsync command to implement sync target.
""")

