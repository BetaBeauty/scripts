from bbcode.common import cmd, log, git

from bbcode import n2n, ssh

@cmd.module("", as_main=True,
            description="""
BBCode Script Tools

This script contains many useful packages, user can invoke
modules with command line flags.

Contact the developer: cunxinshuihua@gmail.com for more support.
""")
def main(args):
    cmd.CmdStorage.get_parser("").print_help()

if __name__ == "__main__":
    log.Init(log.TRACE)
    cmd.Run()
