"""  Local Network Port

OS like unix, mac can not bind to port number lower than 1024
    as a unprivileged user. And these ports are used via
    public and tranditional programs generally, and it's
    strange to transport these ports to remote machines' port.
    Since it's system's duty to disable the TCPServer for
    lower port number, we still should support some portable
    method to implement a single-direction socket data flow.
"""

from os import sys, path
import socket
import getpass
import select
import logging

import paramiko

from bbcode.common import cmd, log

from . import key
from .base import *

logger = logging.getLogger("ssh.map")

def ssh_transport(server, key_file, password):
    user, srv = parse_user(server)
    srv = parse_url(srv, 22)
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    params = { "username": user if user else getpass.getuser(), }

    if path.exists(key_file):
        logger.debug("connecting ssh via private key:{}".format(key_file))
        params["key_filename"] = key_file
    elif password is not None:
        params["password"] = password
    else:
        logger.info("private key:{} not exists".format(key_file))
        params["password"] = getpass.getpass(
            prompt="Please enter password for server:{}".format(server))

    print(params)

    try:
        client.connect(*srv, **params)
    except Exception as e:
        logger.error("Failed to connect to %s:%d - %r" % (*srv, e))
        raise e
        return None

    return client.get_transport()

class LocalServer:
    def __init__(self, address, key_file, password):
        self._user, server = parse_user(address)
        self._server = parse_url(server, 22)

        self._connected = False
        self._sock = None
        if self.is_native():
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect(("localhost", 22))
            self._connected = True
        else:
            self._ts = ssh_transport(
                "{}@{}:{}".format(self._user, self._server[0], 22),
                key_file, password)
            if self._ts:
                srv_address = (socket.gethostname(), 12345)
                self._sock = self._ts.open_channel(
                    kind="direct-tcpip",
                    dest_addr=self._serevr,
                    src_addr=srv_address,
                    timeout=10.0)
                self._connected = True

    def connected(self):
        return self._connected

    def get_channel(self):
        return self._sock

    def sendall(self, data):
        self._sock.sendall(data)

    def is_native(self):
        return self._server[0] in [
            "localhost", "0.0.0.0", "127.0.0.1", "*"]


def communicate(local, remote, info):
    while remote.active:
        rqst, _, _ = select.select([local, remote], [], [], 5)

        if remote in rqst:
            data = remote.recv(1024)
            if not data:
                logger.log(log.TRACE,
                    "server {} send empty data".format(info))
                break
            logger.log(log.TRACE,
                "<<< IN {} recv: {} <<<".format(info, data))
            local.sendall(data)

        if local in rqst:
            data = local.recv(1024)
            if not data:
                logger.log(
                    log.TRACE,
                    "local {} send empty data".format(args.local))
                break
            logger.log(
                log.TRACE,
                ">>> OUT {} send: {} >>>".format(info, data))
            remote.sendall(data)

@cmd.option("--remote", default="0.0.0.0:22",
            help="server listen address, format: host[:port]")
@cmd.option("--local", default="0.0.0.0:22",
            help="local accessable, format: [user:]host[:port]")
@cmd.option("--password", default=None,
            help="server password, this will be prompt if not set")
@cmd.option("server",
            help="ssh server, format: [user:]hostname[:port]")
@cmd.module("ssh.map", as_main=True,
            refs=["ssh.key"],
            help="ssh single direction port map")
def ssh_map(args):
    server_ts = ssh_transport(args.server, args.key_file, args.password)
    local = LocalServer(args.local, args.key_file, args.password)
    if not server_ts or not local.connected():
        return

    remote_address = parse_url(args.remote, 22)
    user, srv = parse_user(args.server)
    srv = parse_url(srv, 22)
    srv_chan = server_ts.open_channel(
        kind="direct-tcpip",
        dest_addr=remote_address,
        src_addr=srv,
        timeout=10.0)

    local_chan = local.get_channel()
    info = '{} - {} - {}'.format(
        args.local, args.server, args.remote)

    try:
        communicate(local_chan, srv_chan, info)
    except Exception as e:
        logger.error("{} interuppt - {}".format(info, e))
    finally:
        local_chan.close()
        srv_chan.close()
        logger.info("{} connection closed".format(info))

    print("done!!!")
