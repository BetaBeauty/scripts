import os
import logging
import getpass
from os import path
from time import sleep
import socketserver

import paramiko
import sshtunnel

from bbcode.common import cmd, thread, log

from . import key
from .base import *

logger = logging.getLogger("ssh.proxy")

SSH_PKEY_FILE = path.join(DEFAULT_SSH_DIRECTORY, "id_rsa")

@cmd.option("--interval", type=int,
            default=10,
            help="ssh tunnel restart interval for unknown error")
@cmd.option("--local", required=True,
            action="append", default=[],
            help="local binding[listen] address, host[:port]")
@cmd.option("--remote", required=True,
            action="append", default=[],
            help="remote listen[binding] address, host[:port]")
@cmd.option("--password", default=None,
            help="server password, this will be prompt if not set")
@cmd.option("--key-file", metavar="FILE",
            default=SSH_PKEY_FILE,
            help="rsa private key, by default load path: ~/.ssh/id_rsa")
@cmd.option("server",
            help="ssh server address, [user@]hostname[:port]")
@cmd.module("ssh.tunnel", as_main=True,
            help="ssh tunnel tools",
            description="""
SSH Tunnel Tools

  By default use formal direction, that is user
    can connect a port of a remote server where only SSH is reachable,
    or want to connect a private server which is ont directly visible
    from the outside:

    port forwarding map:
        local(bind) <- 127.0.0.1 <- server <- remote(listen)
    data flow:
        user -> local -> 127.0.0.1 -> server -> remote

  And for reverse tunnel, refers to the group option: --reverse
""")
def tunnel(args):
    user, server = parse_user(args.server)
    server = parse_url(server, 22)
    los = [parse_url(l, 22) for l in args.local]
    res = [parse_url(r, 22) for r in args.remote]
    tunnel_params = {
        "ssh_username": user,
        "local_bind_addresses": los,
        "remote_bind_addresses": res,
    }

    if path.exists(args.key_file):
        logger.debug("connecting ssh via private key:{}".format(
            args.key_file))
        tunnel_params["ssh_pkey"] = args.key_file
    elif args.password is not None:
        tunnel_params["ssh_password"] = args.password
    else:
        logger.info("private key:{} not exists".format(args.key_file))
        tunnel_params["ssh_password"] = getpass.getpass(
            prompt="Please enter password for server:{}".format(server))

    tunnel = None

    @thread.register_service(
        "ssh tunnel",
        auto_reload=True,
        timeout=args.interval)
    def serve():
        global tunnel

        tunnel = sshtunnel.SSHTunnelForwarder(server, **tunnel_params)
        tunnel.start()
        while tunnel.is_active:
            thread.wait_or_exit(timeout=10)

    @thread.register_stop_handler("ssh tunnel")
    def stop():
        global tunnel
        if tunnel is None:
            return
        tunnel.close()
        tunnel = None
