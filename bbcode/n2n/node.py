import os
from os import path

from bbcode.common import base, git, cmd
from .base import *

@cmd.option("--port", default=None, type=int,
            help="node local UDP port")
@cmd.option("--mana-port", default=None,
            type=int, metavar="PORT",
            help="super/edge node manage port, 5645/5644 by default")
@cmd.option("--debug", action="store_true",
            help="print more node information")
@cmd.option("--usage", action="store_true",
            help="print node usage")
@cmd.module("n2n.node.common",
            description="n2n node common",
            help="n2n node common")
def common_opt(args, bin_path):
    if args.usage:
        base.shell_exec(bin_path, "--help")
        os.sys.exit()

    RUN = ["sudo", bin_path, "-f"]
    if args.mana_port:
        RUN.extend(["-t", args.mana_port])
    if args.port:
        RUN.extend(["-p", args.port])
    if args.debug:
        RUN.append("-v")
    return RUN

@cmd.option("--ip-pools", metavar="NETWORK",
            default="10.2.1.0-10.2.20.0/24",
            help="Subnet range for auto ip address service, e.g. " +
                "-a 192.168.0.0-192.168.255.0/24, defaults to " +
                "10.2.1.0-10.2.20.0/24")
@cmd.module("n2n.super", as_main=True,
            refs=["n2n.common", "n2n.node.common"],
            help="super node execution command")
def super(args):
    build_dir = path.join(git.GIT_ROOT, N2N_NAME, BUILD_DIR)
    bin_path = "" if args.system else build_dir
    bin_path = path.join(bin_path, "supernode")

    RUN = common_opt(args, bin_path)
    RUN.extend(["-a", args.ip_pools])
    base.shell_exec(*RUN)

@cmd.option("--super-url", metavar="URL",
            default="101.200.44.74:7654",
            help="supernode ip:port")
@cmd.option("--key", default="BBCODE_PASSWORD_GUESS",
            help="encryption key (ASCII) - also N2N_KEY=<encrypt key>.")
@cmd.option("--community", metavar="NAME",
            default="BBCODE_FOUNDATION",
            help="n2n community name the edge belongs to")
@cmd.option("--ip", default="-r -a dhcp:0.0.0.0",
            help="n2n ip address, dhcp by default")
@cmd.module("n2n.edge", as_main=True,
            refs=["n2n.common", "n2n.node.common"],
            help="edge node execution command")
def edge(args):
    build_dir = path.join(git.GIT_ROOT, N2N_NAME, BUILD_DIR)
    bin_path = "" if args.system else build_dir
    bin_path = path.join(bin_path, "edge")

    RUN = common_opt(args, bin_path)
    RUN.extend(["-a", args.ip, "-c", args.community,
                "-l", args.super_url,
                "-k", args.key])
    base.shell_exec(*RUN)

