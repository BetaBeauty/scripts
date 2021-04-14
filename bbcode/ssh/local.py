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

from bbcode.common import types
from bbcode.common import cmd, log, thread

from . import key
from .base import *

logger = logging.getLogger("ssh.tunnel.reverse")

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

    try:
        client.connect(*srv, **params)
    except Exception as e:
        logger.error("Failed to connect to %s:%d - %r" % (*srv, e))
        raise e
        return None

    return client.get_transport()

__CHANNELS__ = []
__LOCK__ = threading.Lock()

def handler(chan, local_address, info):
    sock = socket.socket()
    try:
        sock.connect(local_address)
    except Exception as e:
        logger.error("Forwarding request to %s:%d failed - %r" % (
            *local_address, e))
        return

    __CHANNELS__.append(sock)

    logger.debug("Connected! Reverse Tunnel open %s" % info)

    while chan.active:
        rqst, _, _ = select.select([chan, sock], [], [], 5)

        if chan in rqst:
            data = chan.recv(1024)
            if not data:
                logger.log(log.TRACE,
                    "remote {} send empty data".format(info))
                break
            logger.log(log.TRACE,
                "<<< IN {} recv: {} <<<".format(
                    info, types.bytes2hex(data)))
            sock.sendall(data)

        if sock in rqst:
            data = sock.recv(1024)
            if not data:
                logger.log(
                    log.TRACE,
                    "local {} send empty data".format(info))
                break
            logger.log(
                log.TRACE,
                ">>> OUT {} send: {} >>>".format(
                    info, types.bytes2hex(data)))
            chan.sendall(data)

    __LOCK__.acquire()
    if chan in __CHANNELS__:
        __CHANNELS__.remove(chan)
        chan.close()
    if sock in __CHANNELS__:
        __CHANNELS__.remove(sock)
        sock.close()
    __LOCK__.release()

    logger.debug("Tunnel closed for %s" % info)

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
    server_ts = ssh_transport(args.server, args.key_file, args.password)
    if not server_ts:
        return

    los = [parse_url(l, 22) for l in args.local]
    res = [parse_url(r, 22) for r in args.remote]

    for remote_address in res:
        server_ts.request_port_forward(*remote_address)

    @thread.register_service("ssh.tunnel.reverse")
    def start_reverse_tunnel():
        while server_ts.active:
            server_chan = server_ts.accept(10)
            if server_chan is None:
                continue

            __CHANNELS__.append(server_chan)

            for local_addr in los:
                info = "%s:%s - %s" % (*local_addr, args.server)
                thread.as_thread_func(handler)(
                    server_chan, local_addr, info)

    @thread.register_stop_handler("ssh.tunnel.reverse")
    def stop_tunnel_reverse():
        for remote_address in res:
            server_ts.cancel_port_forward(*remote_address)

        server_ts.close()
        server_ts._queue_incoming_channel(None)

        __LOCK__.acquire()
        chan_to_rm = list(__CHANNELS__)
        __CHANNELS__.clear()
        __LOCK__.release()

        for channel in chan_to_rm:
            channel.close()


    thread.Run()

