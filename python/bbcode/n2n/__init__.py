from . import base
from . import install, node, status

from bbcode.common import cmd

@cmd.module("n2n",
            help="n2n inter-connect tools",
            description="n2n inter-connect module, provided a " + \
                "local-network crossing any internet web " + \
                "based on tcp/udp protocols.")
def n2n(args):
    pass
