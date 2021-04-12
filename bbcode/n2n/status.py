from bbcode.common import base, cmd

@cmd.option("--port", default=5645,
            help="listen super/edge node manage port, 5645/5644 by default")
@cmd.option("--ip", default="localhost",
            help="listen node IP address")
@cmd.module("n2n.status", as_main=True,
            description="n2n node status command")
def status(args):
    COM = ["netcat", "-u", args.ip, args.port]
    base.shell_exec(COM)
