import logging
from os import path

from . import base, cmd

GIT_ROOT = ".git_root"

logger = logging.getLogger("git")

cmd.module("git",
           help="git command wrapper tools")

@cmd.option("--git-root",
            default=GIT_ROOT,
            help="git project root directory")
@cmd.option("--branch", default=None,
            help="git branch to checkout")
@cmd.option("name", metavar="NAME", help="git project name")
@cmd.option("url", metavar="URL", help="git clone url")
@cmd.module("git.clone", as_main=True,
            help="git clone wrapper tools",
            description="git clone wrapper tools")
def clone(args):
    base.make_dirs(args.git_root)
    with base.enter(args.git_root):
        if not path.exists(args.name):
            command = ["git", "clone", "--recurse-submodules",
                       args.url, args.name]
            base.shell_exec(
                "git clone --recurse-submodules", args.url, args.name,
                check_error=True)

        if args.branch:
            with base.enter(args.name):
                base.shell_exec("git checkout", args.branch, check_error=True)

@cmd.option("-d", "--delete",
            action="append", default=[],
            help="files to delete")
@cmd.option("-l", "--list-number",
            type=int, default=5,
            help="file numbers to be display, by default 5")
@cmd.option("--git-path", default=".",
            help="git project root path to clean")
@cmd.module("git.clean", as_main=True,
            help="git clean command",
            description="""
Git Clean Tool

By default, this tool will list some biggest files via git command,
and then user will select unuseful files to delete with option:
-d/--delete.
""")
def clean(args):
    for del_file in args.delete:
        logger.info("git delete " + del_file)
        base.shell_exec(
            "git filter-branch --force --index-filter ",
            "\"git rm -rf --cached --ignore-unmatch {}\" ".format(del_file),
            "--prune-empty --tag-name-filter cat -- --all"
        )

    if args.delete:
        logger.info("update all local branches")
        base.shell_exec(
            "git for-each-ref --format='delete %(refname)' refs/original | ",
            "git update-ref --stdin")
        base.shell_exec("git reflog expire --expire=now --all")

        logger.info("start git gc")
        base.shell_exec("git gc --prune=now")
        base.shell_exec("git count-objects -v")

        logger.info("push into remote repository")
        base.shell_exec("git push origin --force --all")
        base.shell_exec("git push origin --force --tags")

    with base.enter(args.git_path):
        logger.info("list large file names")
        base.shell_exec(
            "git verify-pack -v .git/objects/pack/*.idx | ",
            "sort -k 3 -nr | ",
            "head -" + str(args.list_number),
            check_error=True)

        base.shell_exec(
            "git rev-list --objects --all | ",
            "grep",
            "\"$(",
                "git verify-pack -v .git/objects/pack/*.idx | ",
                "sort -k 3 -nr | ",
                "head -" + str(args.list_number) + " | ",
                "awk '{print$1}'",
            ")\"",
            check_error=True)

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
