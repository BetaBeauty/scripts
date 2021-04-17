from bbcode.common import cmd, log, git, thread

from bbcode import n2n, ssh, rsync, os

@cmd.module("", as_main=True,
            description="""
BBCode Script Tools

This script contains many useful packages, user can invoke
modules with command line flags.

Contact the developer: cunxinshuihua@gmail.com for more support.
""")
def main(args):
    cmd.CmdStorage.get_parser("").print_help()

@cmd.option("-v", "--verbosity", metavar="LEVEL",
            choices=log.LOG_NAMES, default=log.level2name(log.DEBUG),
            help="log verbosity to pring information, " + \
                "available options: {}".format(log.LOG_NAMES) + \
                " by default {}".format(log.level2name(log.DEBUG)))
@cmd.prepare()
def prepare_func(args):
    log.Init(log.name2level(args.verbosity))

if __name__ == "__main__":
    cmd.Run()
    # run registered service if possible
    thread.Run()
