from os import path

from . import base, cmd

GIT_ROOT = ".git_root"

@cmd.option("--git-root",
            default=GIT_ROOT,
            help="git project root directory")
@cmd.option("--branch", default=None,
            help="git branch to checkout")
@cmd.option("name", metavar="NAME", help="git project name")
@cmd.option("url", metavar="URL", help="git clone url")
@cmd.module("clone", as_main=True,
            description="git clone sub tools")
def clone(args):
    base.make_dirs(args.git_root)
    with base.enter(args.git_root):
        if not path.exists(args.name):
            command = ["git", "clone", "--recurse-submodules",
                       args.url, args.name]
            base.shell_exec(command, check_error=True)

        if args.branch:
            with base.enter(args.name):
                command = ["git", "checkout", args.branch]
                base.shell_exec(command, check_error=True)

if __name__ == "__main__":
    from . import log

    class Args:
        pass
    args = Args()
    args.url = "git@github.com:BetaBeauty/code_core.git"
    args.name = "test"
    args.branch = "master"
    args.git_root = GIT_ROOT
    log.Init(log.DEBUG)
    clone(args)
