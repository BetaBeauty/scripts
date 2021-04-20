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
import threading

import paramiko

from bbcode.common import base, types
from bbcode.common import cmd, log, thread

from .config import ssh_config
from .base import *

logger = logging.getLogger("ssh.tunnel.reverse")

def ssh_transport(server, key_file, password):
    user, server = parse_user(server)
    server = list(parse_url(server, 22))
    (server[0],
     user,
     key_file,
     port
    ) = ssh_config(server[0],
               username = user,
               private_key = key_file,
               port = server[1])

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    params = { "username": user if user else getpass.getuser(), }

    if password is not None:
        params["password"] = password
    elif path.exists(key_file):
        logger.debug("connecting ssh via private key:{}".format(key_file))
        params["key_filename"] = key_file
    else:
        logger.info("private key:{} not exists".format(key_file))
        params["password"] = getpass.getpass(
            prompt="Please enter password for server:{}".format(server))

    try:
        client.connect(*server, **params)
    except Exception as e:
        logger.error("Failed to connect to %s:%d - %r" % (*server, e))
        raise e
        return None

    ts = client.get_transport()
    ts.set_keepalive(interval=60)
    ts.use_compression(compress=True)
    return ts

__CHANNELS__ = []
__LOCK__ = threading.Lock()

def handler(chan, local_address, info):
    sock = socket.socket()
    try:
        sock.connect(local_address)
    except Exception as e:
        logger.error("connecting to %s:%d failed - %r" % (
            *local_address, e))
        chan.close()
        return

    __LOCK__.acquire()
    __CHANNELS__.append(chan)
    __CHANNELS__.append(sock)
    __LOCK__.release()

    while chan.active:
        rqst, _, _ = select.select([chan, sock], [], [], 5)

        if chan in rqst:
            data = chan.recv(1024)
            if not data:
                break
            sock.sendall(data)

        if sock in rqst:
            data = sock.recv(1024)
            if not data:
                break
            chan.sendall(data)

    __LOCK__.acquire()
    if chan in __CHANNELS__:
        __CHANNELS__.remove(chan)
        chan.close()
    if sock in __CHANNELS__:
        __CHANNELS__.remove(sock)
        sock.close()
    __LOCK__.release()

    logger.info("closing reverse tunnel for %s" % info)

@cmd.group("ssh.tunnel", as_main=True,
           description="""
  Reverse tunnel Group

  User may want to export some local
    address's ports into global internet in some specific
    scenarios, like do reverse tunnel port mapping so that
    developers can access company machines at home as an VPN
    does, but this is somehow a light solution for programmers:

    port forwarding map:
        local(listen) -> 127.0.0.1 -> server -> remote(bind)
    data flow:
        local <- 127.0.0.1 <- server <- remote <- user
""")
def reverse_tunnel(args):
    los = [parse_url(l, 22) for l in args.local]
    res = [parse_url(r, 22) for r in args.remote]

    def forward_handler(channel, remote_addr, server_addr):
        logger.info("connecting reverse tunnel from %s:%d" % (
            remote_addr[0], remote_addr[1]))
        for local_addr in los:
            info = "%s:%s - %s - %s:%d" % (
                *local_addr, args.server, *remote_addr)
            thread.as_thread_func(handler)(
                channel, local_addr, info)

    server_ts = None

    @thread.register_service(
        "ssh.tunnel.reverse",
        auto_reload=True,
        timeout=args.interval)
    def start_tunnel_service():
        global server_ts
        logger.info("ssh reverse tunnel started")
        server_ts = ssh_transport(
            args.server, args.key_file, args.password)
        if not server_ts:
            return

        for remote_address in res:
            server_ts.request_port_forward(
                *remote_address, handler=forward_handler)

        server_ts.accept()

    @thread.register_stop_handler("ssh.tunnel.reverse")
    def stop_tunnel_servive():
        global server_ts
        if not server_ts:
            return

        for remote_address in res:
            server_ts.cancel_port_forward(*remote_address)

        server_ts.close()
        # hook method for quick stop the `Transport.accept`
        server_ts._queue_incoming_channel(None)

        __LOCK__.acquire()
        chan_to_rm = list(__CHANNELS__)
        __CHANNELS__.clear()
        __LOCK__.release()

        for channel in chan_to_rm:
            channel.close()

        server_ts = None
