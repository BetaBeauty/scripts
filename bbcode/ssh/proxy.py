import os
import logging
import getpass
from os import path
from time import sleep
import socketserver

import paramiko
import sshtunnel

from bbcode.common import cmd, url, thread, log

from . import key
from .base import *

logger = logging.getLogger("ssh.proxy")

@cmd.option("--local",
            action="append", default=[],
            )
@cmd.option("--remote",
            action="append", default=[],
            help="server remote bind address: host[:port]")
@cmd.option("--password", default=None,
            help="server password, this will be prompt if not set")
@cmd.option("server",
            help="ssh server, format: [user@]hostname[:port]")
@cmd.module("ssh.tunnel", as_main=True,
            refs=["ssh.key"],
            help="[reverse] proxy for machines")
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

    server = sshtunnel.SSHTunnelForwarder(server, **tunnel_params)

    @thread.register_service("ssh tunnel")
    def serve():
        logger.info("ssh tunnel serving ...")
        server.start()
        while True:
            thread.wait_or_exit(10)

    @thread.register_stop_handler("ssh tunnel")
    def stop():
        server.close()

    thread.Run()

@cmd.group("ssh.tunnel", as_main=True, permission=cmd.PRIVATE)
def test_socket(args):
    import requests

    transport = paramiko.Transport(("101.200.44.74", 22))
    class Handler(sshtunnel._ForwardHandler):
        remote_address = ("101.200.44.74", 8829)
        ssh_transport = transport
    # server = socketserver.TCPServer(
        # # ("127.0.0.1", 22),
        # ("0.0.0.0", 22),
        # Handler)
    sess = requests.session()

    socketserver.UDPServer(
        # ("127.0.0.1", 22),
        ("0.0.0.0", 22),
        Handler)
