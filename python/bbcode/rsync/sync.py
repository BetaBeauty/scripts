import logging
from os import path

from bbcode.common import base, cmd

logger = logging.getLogger("sync.conf")

@cmd.option("--progress",
            action="store_true",
            help="show sync progress")
@cmd.group("rsync.conf", group_name="rsync flags",
           description="rsync common flags")
def sync_impl(source, destination, args):
    if not path.exists(source):
        logger.warning("skip not exists file: %s" % source)
        return

    SYNC = ["rsync"]
    base.shell_exec(
        "rsync -avzch --partial",
        "--progress" if args.progress else "-q",
        source,
        destination,
        check_error=True,
    )

__CONF_REG__ = {}
__CONF_STR__ = ""

INTEGRAL = "integral"
OPTIONAL = "optional"

def register_conf(name, *file_names, group_type=INTEGRAL):
    global __CONF_STR__

    group = __CONF_REG__.setdefault(name, set())
    for f in file_names:
        group.add(f)

    __CONF_STR__ += "\n\t{}\t{}\t{}".format(
        name, group_type, " ".join(file_names))

register_conf("profile",
    ".profile", ".bashrc", ".bash_profile", ".commacd.bash")
register_conf("vim",
    ".vimrc", ".vundle.vim", ".vim")
register_conf("pip", ".config/pip")
register_conf("tmux", ".tmux.conf")
register_conf("conda", ".condarc")
register_conf("aria2", "aria2.conf")
register_conf("git", ".gitconfig")
register_conf("npm",
              ".npm", ".tern-config",
              group_type=OPTIONAL)
register_conf("ssh",
    ".ssh/config", ".ssh/authorized_keys", ".ssh/known_hosts")

@cmd.option("--append",
            action="append", default=[],
            help="add files into sync list")
@cmd.option("--remove",
            action="append", default=[],
            help="remove file from sync list")
@cmd.option("destination", default="~",
            help="destination path, [user@]host:dest")
@cmd.option("source", default="~",
            help="source path, [user@]host:src")
@cmd.module("rsync.conf", as_main=True,
            help="user configuration sync tool",
            description="""
Configuration File Sync Tool

  Configuration Files:
{}

""".format(__CONF_STR__))
def conf_sync(args):

    sync_files = []
    for v in __CONF_REG__.values():
        sync_files.extend(v)

    for r in args.remove:
        files = __CONF_REG__.get(r, None) or [r]
        for f in files:
            sync_files.remove(f)

    for a in args.append:
        files = __CONF_REG__.get(a, None) or [a]
        for f in files:
            sync_files.append(f)

    logger.info("rSync Files:\n\t%s" % " ".join(sync_files))

    dest = args.destination
    if not dest.endswith("/"):
        dest += "/"

    for f in sync_files:
        src = path.join(args.source, f)
        sync_impl(src, dest, args)
