from . import cmd

@cmd.option("-H", "--host", default="127.0.0.1",
            help="url host address, support ip or web name")
@cmd.option("-p", "--port", type=int,
            default=None,
            help="url port number")
@cmd.module("url.common")
def main(args):
    pass
