import logging
from os import path

from bbcode.common import base, cmd, git

from .base import *

logger = logging.getLogger("n2n.status")

@cmd.option("--port", default=5645,
            help="listen super/edge node manage port, 5645/5644 by default")
@cmd.option("--ip", default="localhost",
            help="listen node IP address")
@cmd.module("n2n.status", as_main=True,
            refs=["n2n.common"],
            help="n2n node status command")
def status(args):
    def _info(name, value):
        logger.info("%-20s = %s" % (name, value))

    n2n_root = path.join(git.GIT_ROOT, N2N_NAME)
    _info("N2N ROOT", n2n_root)

    is_download = path.exists(n2n_root)
    _info("IS DOWNLOAD", "True" if is_download else "False")

    build_dir = path.join(n2n_root, BUILD_DIR)
    is_build = path.exists(build_dir)
    _info("IS BUILD", "True" if is_build else "False")

    if is_build:
        _info("BINARY PATH", "SYSTEM" if args.system else build_dir)

    base.shell_exec("netcat -u", args.ip, args.port)
