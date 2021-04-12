import copy
from os import path

from bbcode.common import base, git, cmd
from .base import *

@cmd.option("--branch", default="dev",
            help="n2n project version")
@cmd.group("n2n.install")
def download(args):
    new_args = copy.deepcopy(args)
    new_args.url = "git@github.com:ntop/n2n.git"
    new_args.git_root = git.GIT_ROOT
    new_args.name = N2N_NAME
    new_args.branch = args.branch
    git.clone(new_args)

@cmd.option("--install-dir", metavar="PATH",
            default="/usr",
            help="the system path to be installed for n2n")
@cmd.group("n2n.install")
def compile(args):
    n2n_root = path.join(git.GIT_ROOT, N2N_NAME)
    base.validate(path.exists(n2n_root),
                  "n2n project not exist")
    with base.enter(path.join(n2n_root, BUILD_DIR), create=True):
        CMAKE = ["cmake"]
        if args.system:
            CMAKE.append("-DCMAKE_INSTALL_PREFIX=" + args.install_dir)
        CMAKE.append("..")
        base.shell_exec(CMAKE)

        MAKE = []
        if args.system:
            MAKE.appen("sudo")
        MAKE.extend(["make", "-j${nproc}"])
        if args.system:
            MAKE.append("install")
        base.shell_exec(MAKE)

N2N_CONF_DIR = "n2n/etc"

def install_conf(args):
    CP = ["sudo cp -r", N2N_CONF_DIR, "/"]
    base.shell_exec(CP)

    RELOAD = ["sudo systemctl daemon-reload"]
    base.shell_exec(RELOAD)

    UPDATE = ["sudo update-rc.d n2n defaults"]
    base.shell_exec(update)

def remove_conf(args):
    RELOAD = ["sudo systemctl stop n2n"]
    base.shell_exec(RELOAD)

    RM = ["sudo rm -rf /etc/init.d/n2n"]
    base.shell_exec(RM)

@cmd.module("n2n.install", refs=["n2n.common"], as_main=True,
            description="n2n install sub command")
def install(args):
    download(args)

    n2n_root = path.join(git.GIT_ROOT, N2N_NAME)
    build_dir = path.join(n2n_root, BUILD_DIR)
    compile(args)

    if args.system:
        install_conf(args)

