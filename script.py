from bbcode.common import cmd, log, git

from bbcode import n2n

@cmd.module("", as_main=True,
            description="bbcode script tools")
def main(args):
    cmd.CmdStorage.get_parser("").print_help()

if __name__ == "__main__":
    log.Init(log.DEBUG)
    cmd.Run()
