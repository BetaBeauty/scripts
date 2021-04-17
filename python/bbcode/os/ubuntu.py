import logging
import subprocess

from bbcode.common import base, cmd
from bbcode.common.types import *

SRC_LISTS = {
    "tsinghua" : """
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name} main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name} main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ {code_name}-proposed main restricted universe multiverse
""",
    "aliyun" : """
deb http://mirrors.aliyun.com/ubuntu/ {code_name} main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {code_name}-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {code_name}-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {code_name}-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ {code_name}-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ {code_name} main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ {code_name}-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ {code_name}-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ {code_name}-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ {code_name}-backports main restricted universe multiverse
"""}

SRC_KEYS = list(SRC_LISTS.keys())

logger = logging.getLogger("os.ubuntu")

@cmd.option("--source",
            choices=SRC_KEYS, default=SRC_KEYS[0],
            help="".join([
                "system package source, available options: {}, ".format(
                    ",".join(SRC_KEYS)),
                "by default {}".format(SRC_KEYS[0]),
            ]))
@cmd.module("ubuntu.install")
def source_substutiation(args):
    src_path = "/etc/apt/sources.list"
    with open(src_path, "r") as f:
        ori_src = f.read()

    code_name = base.check_output("lsb_release", "-c", "-s")
    code_name = bytes2str(code_name).strip()

    src = SRC_LISTS[args.source].format(code_name=code_name)
    if args.source in ori_src:
        logger.info("source list has aleady been: {}".format(
            args.source))
        return

    logger.debug("backup source list file into {}.bak".format(src_path))
    base.shell_exec(
        "sudo mv {fpath} {fpath}.bak".format(fpath=src_path))
    logger.debug("write new source to file: {}".format(src_path))
    tmp_path = "/tmp/{}".format(src_path)
    with open(tmp_path, "w") as f:
        f.write(src)
    base.shell_exec(
        "sudo mv {} {}".format(tmp_path, src_path))

def system_install(*names):
    for name in names:
        base.shell_exec("sudo apt install", name)

@cmd.group("ubuntu.install", as_main=True,
           description=" ".join([
            "mini conda installer, download installer from",
            "official miniconda website:",
            "\nhttps://docs.conda.io/en/latest/miniconda.html#linux-installers"
           ]))
def conda(args):
    conda_name = "Miniconda3-latest-Linux-x86_64.sh"
    base.shell_exec(
        "wget https://repo.anaconda.com/miniconda/",
        conda_name)
    base.shell_exec("bash", conda_name)

@cmd.module("ubuntu.install", as_main=True,
            help="ubuntu install tool",
            description="""
Ubuntu Install Module

  Things to do for initialize system:
    1. replace system source.list
""")
def ubuntu_install(args):
    source_substutiation(args)

    base.shell_exec("sudo apt update")
    base.shell_exec("sudo apt upgrade")

    system_install("python-dev", "build_essential")
    system_install("make", "cmake", "vim", "git")
    system_install("rsync", "ssh")
    system_install("tmux")

